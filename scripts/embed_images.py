"""Embed images with Marqo-FashionSigLIP-v1, streaming downloads.

Usage:
  python scripts/embed_images.py --source musinsa --limit 20             # smoke test
  python scripts/embed_images.py --source musinsa
  python scripts/embed_images.py --source runway_tagwalk
  python scripts/embed_images.py --source product
  python scripts/embed_images.py --source runway_vogue                   # 26SS+26FW+25FW only
  python scripts/embed_images.py --source all
"""
from __future__ import annotations

import argparse
import io
import json
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import requests
import torch
import open_clip
from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "backend" / "db" / "ftib.db"
MODEL_NAME = "hf-hub:Marqo/marqo-fashionSigLIP"
MODEL_VERSION = "marqo-fashionSigLIP-v1"
VOGUE_SEASONS = ("spring-summer-2026", "fall-winter-2026", "fall-winter-2025")

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
HEADERS = {"User-Agent": UA, "Accept": "image/*,*/*;q=0.8"}


def fetch_image(url: str, timeout: int = 15) -> Image.Image:
    r = requests.get(url, timeout=timeout, headers=HEADERS)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")


SOURCES = {
    "musinsa": {
        "table": "musinsa_products",
        "id_col": "id",
        "url_expr": "image_url",
        "where": "image_url IS NOT NULL AND image_url != ''",
        "url_is_json": False,
    },
    "runway_tagwalk": {
        "table": "runway_looks",
        "id_col": "id",
        "url_expr": "image_url",
        "where": "image_url IS NOT NULL AND image_url != ''",
        "url_is_json": False,
    },
    "runway_vogue": {
        "table": "vogue_runway_images",
        "id_col": "id",
        "url_expr": "image_url",
        "where": "image_url IS NOT NULL AND image_url != '' AND season IN "
                 f"({','.join('?' * len(VOGUE_SEASONS))})",
        "where_params": VOGUE_SEASONS,
        "url_is_json": False,
    },
    "product": {
        "table": "products",
        "id_col": "id",
        "url_expr": "image_urls",
        "where": "image_urls IS NOT NULL AND image_urls != '' AND image_urls != '[]'",
        "url_is_json": True,
    },
}


def iter_pending(conn: sqlite3.Connection, source: str):
    """Yield (source_id, image_url) pairs that haven't been embedded yet."""
    cfg = SOURCES[source]
    params = list(cfg.get("where_params", ()))
    sql = (
        f"SELECT {cfg['id_col']}, {cfg['url_expr']} FROM {cfg['table']} "
        f"WHERE {cfg['where']}"
    )
    cur = conn.execute(sql, params)
    seen = set()
    cur2 = conn.execute(
        "SELECT source_id, image_url FROM image_embeddings WHERE source_type = ? AND model_version = ?",
        (source, MODEL_VERSION),
    )
    done = {(sid, url) for sid, url in cur2}
    cur3 = conn.execute(
        "SELECT source_id, image_url FROM image_embedding_failures WHERE source_type = ? AND model_version = ?",
        (source, MODEL_VERSION),
    )
    done |= {(sid, url) for sid, url in cur3}

    for sid, raw in cur:
        if cfg["url_is_json"]:
            try:
                urls = json.loads(raw) if isinstance(raw, str) else raw
            except json.JSONDecodeError:
                continue
            if not isinstance(urls, list):
                continue
        else:
            urls = [raw]
        for u in urls:
            if not u or not isinstance(u, str):
                continue
            key = (str(sid), u)
            if key in done or key in seen:
                continue
            seen.add(key)
            yield key


def download_one(item):
    sid, url = item
    try:
        img = fetch_image(url)
        return ("ok", sid, url, img)
    except (requests.RequestException, UnidentifiedImageError, OSError) as e:
        return ("err", sid, url, str(e)[:200])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True,
                   choices=list(SOURCES) + ["all"])
    p.add_argument("--limit", type=int, default=None,
                   help="Max images to process (for smoke test)")
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--workers", type=int, default=12,
                   help="Parallel download workers")
    p.add_argument("--dry-run", action="store_true",
                   help="Skip DB writes; just measure throughput")
    args = p.parse_args()

    sources = list(SOURCES) if args.source == "all" else [args.source]

    print(f"Loading {MODEL_NAME} on CPU...")
    t0 = time.time()
    model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME)
    model.eval()
    print(f"  loaded in {time.time()-t0:.1f}s")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")

    for src in sources:
        print(f"\n=== Source: {src} ===")
        pending = list(iter_pending(conn, src))
        if args.limit:
            pending = pending[: args.limit]
        n_total = len(pending)
        if not n_total:
            print("  (nothing to do)")
            continue
        print(f"  {n_total:,} images to embed")

        ok = fail = 0
        t_start = time.time()
        last_log = t_start

        # Producer: parallel downloads → consumer: GPU/CPU batched embed
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures_iter = pool.map(download_one, pending, chunksize=4)
            buffer_imgs, buffer_meta = [], []
            buffer_fail = []

            def flush():
                nonlocal ok
                if not buffer_imgs:
                    return
                tens = torch.stack([preprocess(im) for im in buffer_imgs])
                with torch.no_grad():
                    feats = model.encode_image(tens)
                    feats = feats / feats.norm(dim=-1, keepdim=True)
                arr = feats.cpu().numpy().astype(np.float32)
                if not args.dry_run:
                    rows = [
                        (src, sid, url, MODEL_VERSION, arr.shape[1], arr[i].tobytes())
                        for i, (sid, url) in enumerate(buffer_meta)
                    ]
                    conn.executemany(
                        "INSERT OR IGNORE INTO image_embeddings "
                        "(source_type, source_id, image_url, model_version, embed_dim, embedding) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        rows,
                    )
                    conn.commit()
                ok += len(buffer_imgs)
                buffer_imgs.clear()
                buffer_meta.clear()

            def flush_failures():
                nonlocal fail
                if not buffer_fail:
                    return
                if not args.dry_run:
                    conn.executemany(
                        "INSERT OR IGNORE INTO image_embedding_failures "
                        "(source_type, source_id, image_url, model_version, error) "
                        "VALUES (?, ?, ?, ?, ?)",
                        [(src, sid, url, MODEL_VERSION, err)
                         for sid, url, err in buffer_fail],
                    )
                    conn.commit()
                fail += len(buffer_fail)
                buffer_fail.clear()

            for status, sid, url, payload in futures_iter:
                if status == "ok":
                    buffer_imgs.append(payload)
                    buffer_meta.append((sid, url))
                    if len(buffer_imgs) >= args.batch_size:
                        flush()
                else:
                    buffer_fail.append((sid, url, payload))
                    if len(buffer_fail) >= 50:
                        flush_failures()

                done = ok + fail + len(buffer_imgs) + len(buffer_fail)
                if time.time() - last_log > 5:
                    rate = done / (time.time() - t_start)
                    eta = (n_total - done) / rate if rate else 0
                    print(f"  [{done:>5}/{n_total}] ok={ok} fail={fail} "
                          f"rate={rate:.1f}/s eta={eta/60:.1f}m")
                    last_log = time.time()

            flush()
            flush_failures()

        dt = time.time() - t_start
        print(f"  done: ok={ok} fail={fail} in {dt:.1f}s ({n_total/dt:.1f} img/s)")

    conn.close()


if __name__ == "__main__":
    main()
