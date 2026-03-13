"""VLM Labels API — VLM 라벨링 결과 조회."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends
import aiosqlite

from backend.db.database import get_db

router = APIRouter()


@router.get("")
async def get_vlm_labels(db: aiosqlite.Connection = Depends(get_db)):
    """VLM 라벨링 완료된 룩 + 이미지 정보 조회."""
    rows = await db.execute_fetchall("""
        SELECT
            vl.id, vl.source_id, vl.items, vl.overall_silhouette,
            vl.dominant_colors, vl.key_materials, vl.model_used, vl.created_at,
            rl.designer, rl.season, rl.look_number, rl.image_url, rl.thumbnail_url
        FROM vlm_labels vl
        JOIN runway_looks rl ON rl.id = vl.source_id
        ORDER BY rl.designer, rl.season, rl.look_number
    """)

    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "source_id": r[1],
            "items": json.loads(r[2]) if r[2] else [],
            "overall_silhouette": r[3],
            "dominant_colors": json.loads(r[4]) if r[4] else [],
            "key_materials": json.loads(r[5]) if r[5] else [],
            "model_used": r[6],
            "created_at": r[7],
            "designer": r[8],
            "season": r[9],
            "look_number": r[10],
            "image_url": r[11],
            "thumbnail_url": r[12],
        })

    return results
