"""Vogue Runway API 라우트."""
from __future__ import annotations

from typing import Optional

import aiosqlite
from fastapi import APIRouter, Depends, Query

from backend.db.database import get_db

router = APIRouter(prefix="/vogue-runway", tags=["vogue-runway"])


@router.get("/shows")
async def get_shows(
    designer_slug: Optional[str] = None,
    season: Optional[str] = None,
    collection_type: Optional[str] = None,
    db: aiosqlite.Connection = Depends(get_db),
):
    """쇼 목록 조회."""
    q = "SELECT * FROM vogue_shows WHERE 1=1"
    params: list = []
    if designer_slug:
        q += " AND designer_slug = ?"
        params.append(designer_slug)
    if season:
        q += " AND season = ?"
        params.append(season)
    if collection_type:
        q += " AND collection_type = ?"
        params.append(collection_type)
    q += " ORDER BY designer, season_slug"
    rows = await db.execute(q, params)
    results = await rows.fetchall()
    return [dict(r) for r in results]


@router.get("/shows/{show_id:path}")
async def get_show_detail(
    show_id: str,
    db: aiosqlite.Connection = Depends(get_db),
):
    """쇼 상세 + 이미지 목록."""
    show_row = await db.execute("SELECT * FROM vogue_shows WHERE id = ?", [show_id])
    show = await show_row.fetchone()
    if not show:
        return {"error": "Show not found"}

    img_rows = await db.execute(
        "SELECT * FROM vogue_runway_images WHERE show_id = ? ORDER BY image_type, look_number",
        [show_id],
    )
    images = await img_rows.fetchall()
    return {
        "show": dict(show),
        "images": [dict(r) for r in images],
    }


@router.get("/images")
async def get_images(
    designer_slug: Optional[str] = None,
    season: Optional[str] = None,
    image_type: Optional[str] = None,
    limit: int = Query(default=200, le=1000),
    offset: int = Query(default=0),
    db: aiosqlite.Connection = Depends(get_db),
):
    """이미지 검색."""
    q = "SELECT * FROM vogue_runway_images WHERE 1=1"
    params: list = []
    if designer_slug:
        q += " AND designer_slug = ?"
        params.append(designer_slug)
    if season:
        q += " AND season = ?"
        params.append(season)
    if image_type:
        q += " AND image_type = ?"
        params.append(image_type)
    q += " ORDER BY designer_slug, season, image_type, look_number"
    q += f" LIMIT {limit} OFFSET {offset}"
    rows = await db.execute(q, params)
    results = await rows.fetchall()
    return [dict(r) for r in results]


@router.get("/stats")
async def get_stats(db: aiosqlite.Connection = Depends(get_db)):
    """전체 통계."""
    shows = await (await db.execute("SELECT COUNT(*) FROM vogue_shows")).fetchone()
    images = await (await db.execute(
        "SELECT image_type, COUNT(*) as cnt FROM vogue_runway_images GROUP BY image_type"
    )).fetchall()
    return {
        "total_shows": shows[0],
        "images_by_type": {r["image_type"]: r["cnt"] for r in images},
        "total_images": sum(r["cnt"] for r in images),
    }
