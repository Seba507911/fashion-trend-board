"""런웨이 API 라우터."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
import aiosqlite

from backend.db.database import get_db

router = APIRouter()


@router.get("")
async def list_runway_looks(
    designer: Optional[str] = None,
    season: Optional[str] = None,
    collection_type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(default=60, le=200),
    offset: int = 0,
    db: aiosqlite.Connection = Depends(get_db),
):
    """런웨이 룩 목록."""
    query = "SELECT * FROM runway_looks WHERE 1=1"
    params: list = []

    if designer:
        query += " AND designer_slug = ?"
        params.append(designer)
    if season:
        query += " AND season = ?"
        params.append(season)
    if collection_type:
        query += " AND collection_type = ?"
        params.append(collection_type)
    if tag:
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")

    query += " ORDER BY designer_slug, season DESC, look_number ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@router.get("/designers")
async def list_designers(db: aiosqlite.Connection = Depends(get_db)):
    """런웨이 디자이너 목록 (룩 수 포함)."""
    cursor = await db.execute("""
        SELECT designer_slug, designer, COUNT(*) as look_count,
               GROUP_CONCAT(DISTINCT season) as seasons
        FROM runway_looks
        GROUP BY designer_slug
        ORDER BY designer
    """)
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@router.get("/seasons")
async def list_seasons(db: aiosqlite.Connection = Depends(get_db)):
    """사용 가능한 시즌 목록."""
    cursor = await db.execute("""
        SELECT DISTINCT season, season_label
        FROM runway_looks
        ORDER BY season DESC
    """)
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]
