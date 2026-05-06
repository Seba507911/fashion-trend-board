"""Retry image_embedding_failures with URL normalization + transient retry.

Categories handled:
  1. protocol-relative `//domain/path`           → prepend `https:`
  2. absolute-path `/web/...`                    → use product's product_url to derive base (skip UI icons)
  3. transient (HTTP 502 / 5xx / Connection)     → retry as-is
  4. HTTP 404 / 410                              → permanent, skip

Usage:
  python scripts/retry_failed_embeddings.py --dry-run     # show plan only
  python scripts/retry_failed_embeddings.py
"""
from __future__ import annotations

import argparse
import io
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import requests
import torch
import open_clip
from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "backend" / "db" / "ftib.db"
MODEL_NAME = "hf-hub:Marqo/marqo-fashionSigLIP"
MODEL_VERSION = "marqo-fashionSigLIP-v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "image/*,*/*;q=0.8",
}


def base_origin(product_url: str) -> str:
    """Return scheme://host of a product_url for resolving root-relative paths."""
    if not product_url:
        return ""
    p = urlparse(product_url)
    if p.scheme and p.netloc:
        return f"{p.scheme}://{p.netloc}"
    return ""


def normalize_failure(url: str, error: str, product_url: str) -> tuple[str | None, str]:
    """Return (new_url_or_None, reason). None means skip permanently."""
    is_invalid = "Invalid URL" in (error or "")
    is_404 = "404" in (error or "")
    is_410 = "410" in (error or "")
    if is_404 or is_410:
        return None, "permanent_4xx"

    if is_invalid:
        if url.startswith("//"):
            return "https:" + url, "fix_protocol_relative"
        if url.startswith("/"):
            # UI icons are not real product images
            if "/web/upload/icon_" in url or url.endswith((".ico",)):
                return None, "skip_ui_icon"
            origin = base_origin(product_url)
            if origin:
                return origin + url, "fix_absolute_path"
            return None, "no_base_url"
        return None, "unknown_invalid"

    # transient errors → retry as-is
    return url, "transient_retry"


def fetch_image(url: str, timeout: int = 15) -> Image.Image:
    r = requests.get(url, timeout=timeout, headers=HEADERS)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")


def download_one(item):
    sid, url, fail_id = item
    try:
        return ("ok", sid, url, fail_id, fetch_image(url))
    except (requests.RequestException, UnidentifiedImageError, OSError) as e:
        return ("err", sid, url, fail_id, str(e)[:200])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--workers", type=int, default=12)
    p.add_argument("--batch-size", type=int, default=16)
    args = p.parse_args()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Load all failures with product_url for base resolution
    cur.execute("""
        SELECT f.id, f.source_id, f.image_url, f.error, p.product_url
        FROM image_embedding_failures f
        LEFT JOIN products p ON p.id = f.source_id
        WHERE f.source_type = 'product' AND f.model_version = ?
    """, (MODEL_VERSION,))
    rows = cur.fetchall()
    print(f"Total failure rows: {len(rows):,}")

    plan = {"fix_protocol_relative": [], "fix_absolute_path": [],
            "transient_retry": [], "skip_ui_icon": [],
            "permanent_4xx": [], "no_base_url": [], "unknown_invalid": []}

    for fail_id, sid, url, err, prod_url in rows:
        new_url, reason = normalize_failure(url, err, prod_url or "")
        plan[reason].append((fail_id, sid, url, new_url))

    print("\n=== Plan ===")
    for k, items in plan.items():
        print(f"  {k:25s}  {len(items):>5,}")

    retry_items = (plan["fix_protocol_relative"]
                   + plan["fix_absolute_path"]
                   + plan["transient_retry"])
    skip_perm_items = (plan["skip_ui_icon"]
                       + plan["permanent_4xx"]
                       + plan["no_base_url"]
                       + plan["unknown_invalid"])

    print(f"\n  → will retry:      {len(retry_items):,}")
    print(f"  → will mark skip:  {len(skip_perm_items):,}")

    if args.dry_run:
        print("\n(dry-run, exiting)")
        return

    # Mark permanent skips with a clearer error tag (don't delete — keep audit trail)
    if skip_perm_items:
        conn.executemany(
            "UPDATE image_embedding_failures SET error = 'SKIP: ' || error WHERE id = ?",
            [(it[0],) for it in skip_perm_items if not (it[2] or '').startswith('SKIP:')],
        )
        conn.commit()

    if not retry_items:
        print("Nothing to retry.")
        return

    print(f"\nLoading {MODEL_NAME}...")
    model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME)
    model.eval()

    work = [(sid, new_url, fid) for (fid, sid, _orig, new_url) in retry_items]

    ok = fail = 0
    t0 = time.time()
    last_log = t0

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures_iter = pool.map(download_one, work, chunksize=4)
        buf_imgs, buf_meta, buf_fail = [], [], []

        def flush():
            nonlocal ok
            if not buf_imgs:
                return
            tens = torch.stack([preprocess(im) for im in buf_imgs])
            with torch.no_grad():
                feats = model.encode_image(tens)
                feats = feats / feats.norm(dim=-1, keepdim=True)
            arr = feats.cpu().numpy().astype(np.float32)
            rows_ins = [
                ("product", sid, url, MODEL_VERSION, arr.shape[1], arr[i].tobytes())
                for i, (sid, url, _fid) in enumerate(buf_meta)
            ]
            conn.executemany(
                "INSERT OR IGNORE INTO image_embeddings "
                "(source_type, source_id, image_url, model_version, embed_dim, embedding) "
                "VALUES (?,?,?,?,?,?)",
                rows_ins,
            )
            # Remove from failures only on success
            conn.executemany(
                "DELETE FROM image_embedding_failures WHERE id = ?",
                [(fid,) for _sid, _url, fid in buf_meta],
            )
            conn.commit()
            ok += len(buf_imgs)
            buf_imgs.clear(); buf_meta.clear()

        def flush_fail():
            nonlocal fail
            if not buf_fail:
                return
            # Update error message; keep the row
            conn.executemany(
                "UPDATE image_embedding_failures SET error = ?, image_url = ?, failed_at = CURRENT_TIMESTAMP WHERE id = ?",
                [(err, new_url, fid) for new_url, err, fid in buf_fail],
            )
            conn.commit()
            fail += len(buf_fail)
            buf_fail.clear()

        for status, sid, url, fid, payload in futures_iter:
            if status == "ok":
                buf_imgs.append(payload)
                buf_meta.append((sid, url, fid))
                if len(buf_imgs) >= args.batch_size:
                    flush()
            else:
                buf_fail.append((url, payload, fid))
                if len(buf_fail) >= 50:
                    flush_fail()

            done = ok + fail + len(buf_imgs) + len(buf_fail)
            if time.time() - last_log > 5:
                rate = done / (time.time() - t0)
                eta = (len(work) - done) / rate if rate else 0
                print(f"  [{done:>5}/{len(work)}] ok={ok} fail={fail} "
                      f"rate={rate:.1f}/s eta={eta/60:.1f}m")
                last_log = time.time()

        flush()
        flush_fail()

    dt = time.time() - t0
    print(f"\nDone: recovered={ok}, still-failed={fail}, in {dt:.1f}s ({len(work)/dt:.1f} img/s)")


if __name__ == "__main__":
    main()
