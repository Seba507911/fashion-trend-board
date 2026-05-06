"""Image embedding explorer API.

Loads all stored Marqo-FashionSigLIP-v1 embeddings into memory once, then
serves stats / random picks / cosine-similarity searches.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock
from typing import Optional

import numpy as np
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])

DB_PATH = Path(__file__).resolve().parents[3] / "backend" / "db" / "ftib.db"
MODEL_VERSION = "marqo-fashionSigLIP-v1"
_LOCK = Lock()
_INDEX = None  # dict: emb (N,768), ids list of (db_id, source_type, source_id, image_url)


def _load_index():
    global _INDEX
    with _LOCK:
        if _INDEX is not None:
            return _INDEX
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        # Brand keys per source — designer for runway, brand_id/slug for market
        brand_keys: dict[tuple, str] = {}
        cur.execute("SELECT id, designer FROM runway_looks")
        for sid, d in cur:
            brand_keys[("runway_tagwalk", sid)] = (d or "").lower().strip()
        cur.execute("SELECT id, designer FROM vogue_runway_images")
        for sid, d in cur:
            brand_keys[("runway_vogue", sid)] = (d or "").lower().strip()
        cur.execute("SELECT id, brand_id FROM products")
        for sid, b in cur:
            brand_keys[("product", sid)] = (b or "").lower().strip()
        cur.execute("SELECT id, brand_slug FROM musinsa_products")
        for sid, b in cur:
            brand_keys[("musinsa", sid)] = (b or "").lower().strip()

        cur.execute(
            "SELECT id, source_type, source_id, image_url, embed_dim, embedding "
            "FROM image_embeddings WHERE model_version = ? ORDER BY id",
            (MODEL_VERSION,),
        )
        ids: list[tuple] = []   # (db_id, source_type, source_id, image_url, brand_key)
        embs: list[np.ndarray] = []
        for db_id, src, sid, url, dim, blob in cur:
            embs.append(np.frombuffer(blob, dtype=np.float32))
            ids.append((db_id, src, sid, url, brand_keys.get((src, sid), "")))
        conn.close()
        emb_mat = np.stack(embs).astype(np.float32) if embs else np.zeros((0, 768), dtype=np.float32)
        id_to_row = {db_id: i for i, (db_id, *_rest) in enumerate(ids)}
        # Vectorized brand array for fast masking
        brand_arr = np.array([b for *_r, b in ids], dtype=object)
        src_arr = np.array([s for _i, s, *_r in ids], dtype=object)
        _INDEX = {
            "emb": emb_mat, "ids": ids, "id_to_row": id_to_row,
            "brand_arr": brand_arr, "src_arr": src_arr,
        }
        return _INDEX


def _display_info(items: list[tuple]) -> dict:
    """For a list of (db_id, src, sid, url), batch-fetch display info per source."""
    by_src: dict[str, list[str]] = {}
    for _, src, sid, _url in items:
        by_src.setdefault(src, []).append(sid)

    info: dict[tuple, dict] = {}
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if "musinsa" in by_src:
        ids = by_src["musinsa"]
        ph = ",".join("?" * len(ids))
        cur.execute(
            f"SELECT id, brand_name, product_name, category FROM musinsa_products WHERE id IN ({ph})",
            ids,
        )
        for sid, brand, name, cat in cur:
            info[("musinsa", sid)] = {"brand": brand, "name": name, "category": cat}
    if "product" in by_src:
        ids = by_src["product"]
        ph = ",".join("?" * len(ids))
        cur.execute(
            f"SELECT id, brand_id, product_name FROM products WHERE id IN ({ph})",
            ids,
        )
        for sid, brand, name in cur:
            info[("product", sid)] = {"brand": brand, "name": name}
    if "runway_tagwalk" in by_src:
        ids = by_src["runway_tagwalk"]
        ph = ",".join("?" * len(ids))
        cur.execute(
            f"SELECT id, designer, season, look_number FROM runway_looks WHERE id IN ({ph})",
            ids,
        )
        for sid, designer, season, look in cur:
            info[("runway_tagwalk", sid)] = {
                "designer": designer, "season": season, "look_number": look,
            }
    if "runway_vogue" in by_src:
        ids = by_src["runway_vogue"]
        ph = ",".join("?" * len(ids))
        cur.execute(
            f"SELECT id, designer, season, look_number FROM vogue_runway_images WHERE id IN ({ph})",
            ids,
        )
        for sid, designer, season, look in cur:
            info[("runway_vogue", sid)] = {
                "designer": designer, "season": season, "look_number": look,
            }
    conn.close()
    return info


def _serialize(items: list[tuple], scores: Optional[list[float]] = None) -> list[dict]:
    # items entries are (db_id, source_type, source_id, image_url, brand_key) — strip brand for display
    items_4 = [it[:4] for it in items]
    info = _display_info(items_4)
    out = []
    for i, (db_id, src, sid, url, *_rest) in enumerate(items):
        d = {
            "id": db_id, "source_type": src, "source_id": sid, "image_url": url,
            **(info.get((src, sid)) or {}),
        }
        if scores is not None:
            d["similarity"] = float(scores[i])
        out.append(d)
    return out


@router.get("/stats")
def stats():
    """Coverage stats by source."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT source_type, COUNT(*) FROM image_embeddings WHERE model_version = ? GROUP BY source_type",
        (MODEL_VERSION,),
    )
    embedded = {src: n for src, n in cur}
    cur.execute(
        "SELECT source_type, COUNT(*) FROM image_embedding_failures "
        "WHERE model_version = ? AND error NOT LIKE 'SKIP:%' GROUP BY source_type",
        (MODEL_VERSION,),
    )
    failed = {src: n for src, n in cur}
    cur.execute(
        "SELECT source_type, COUNT(*) FROM image_embedding_failures "
        "WHERE model_version = ? AND error LIKE 'SKIP:%' GROUP BY source_type",
        (MODEL_VERSION,),
    )
    skipped = {src: n for src, n in cur}
    conn.close()
    sources = sorted(set(embedded) | set(failed) | set(skipped))
    rows = [{
        "source_type": s,
        "embedded": embedded.get(s, 0),
        "failed": failed.get(s, 0),
        "skipped": skipped.get(s, 0),
    } for s in sources]
    return {
        "model_version": MODEL_VERSION,
        "total_embedded": sum(embedded.values()),
        "rows": rows,
    }


@router.get("/picks")
def picks(source_type: str, n: int = Query(default=12, le=48)):
    """Random sample of embedded items from a source — for the picker UI."""
    idx = _load_index()
    rows = [it for it in idx["ids"] if it[1] == source_type]
    if not rows:
        return []
    n = min(n, len(rows))
    chosen = list(np.random.default_rng().choice(len(rows), size=n, replace=False))
    items = [rows[i] for i in chosen]
    return _serialize(items)


def _similarity_search(
    row: int,
    top: int,
    filter_source: Optional[str],
    exclude_self_source: bool,
    exclude_same_brand: bool,
):
    """Shared core: returns (top_indices, scores) given query row index."""
    idx = _load_index()
    q = idx["emb"][row:row+1]
    sims = (idx["emb"] @ q.T).reshape(-1).copy()
    sims[row] = -1

    mask = np.ones(len(sims), dtype=bool)
    if filter_source:
        mask &= (idx["src_arr"] == filter_source)
    if exclude_self_source:
        self_src = idx["ids"][row][1]
        mask &= (idx["src_arr"] != self_src)
    if exclude_same_brand:
        self_brand = idx["ids"][row][4]
        if self_brand:
            mask &= ~((idx["brand_arr"] == self_brand) & (idx["src_arr"] == idx["ids"][row][1]))

    sims_masked = np.where(mask, sims, -1.0)
    k = min(top, int(mask.sum()))
    if k <= 0:
        return [], []
    top_idx = np.argpartition(-sims_masked, k - 1)[:k]
    top_idx = top_idx[np.argsort(-sims_masked[top_idx])]
    return top_idx.tolist(), [float(sims_masked[i]) for i in top_idx]


@router.get("/similar")
def similar(
    id: int,
    top: int = Query(default=12, le=50),
    filter_source: Optional[str] = None,
    exclude_self_source: bool = False,
    exclude_same_brand: bool = True,
):
    """Cosine-similarity search for a query embedding by db id."""
    idx = _load_index()
    row = idx["id_to_row"].get(id)
    if row is None:
        raise HTTPException(404, f"embedding id {id} not found")

    top_idx, scores = _similarity_search(
        row, top, filter_source, exclude_self_source, exclude_same_brand,
    )
    items = [idx["ids"][i] for i in top_idx]
    query_item = _serialize([idx["ids"][row]])[0]
    return {"query": query_item, "results": _serialize(items, scores)}


@router.get("/graph")
def graph(
    id: int,
    top: int = Query(default=15, le=40),
    filter_source: Optional[str] = None,
    exclude_self_source: bool = False,
    exclude_same_brand: bool = True,
    min_edge_sim: float = Query(default=0.75, ge=0.0, le=1.0),
):
    """Return a node+edge graph: query at center, top-K results, edges among
    every pair (including query) whose cosine similarity >= min_edge_sim.
    """
    idx = _load_index()
    row = idx["id_to_row"].get(id)
    if row is None:
        raise HTTPException(404, f"embedding id {id} not found")

    top_idx, q_scores = _similarity_search(
        row, top, filter_source, exclude_self_source, exclude_same_brand,
    )
    all_rows = [row] + top_idx
    sub = idx["emb"][all_rows]
    pair = sub @ sub.T
    # Build links: query↔result always (with score), result↔result if >= min_edge_sim
    nodes_data = _serialize([idx["ids"][r] for r in all_rows])
    nodes = []
    for i, n in enumerate(nodes_data):
        nodes.append({
            "id": n["id"],
            "label": (
                n.get("designer") or n.get("brand") or n["source_type"]
            ),
            "image_url": n["image_url"],
            "source_type": n["source_type"],
            "is_query": i == 0,
            "similarity_to_query": float(pair[0, i]) if i > 0 else 1.0,
            "meta": {k: v for k, v in n.items()
                     if k not in ("id", "image_url", "source_type")},
        })

    links = []
    n = len(all_rows)
    for i in range(n):
        for j in range(i + 1, n):
            s = float(pair[i, j])
            # Always keep query↔result links so node is connected
            if i == 0 or s >= min_edge_sim:
                links.append({
                    "source": nodes[i]["id"],
                    "target": nodes[j]["id"],
                    "value": s,
                })
    return {"nodes": nodes, "links": links}
