"""브랜드 API 라우터."""
from typing import Optional
from fastapi import APIRouter, Depends
import aiosqlite

from backend.db.database import get_db

router = APIRouter()


@router.get("")
async def list_brands(db: aiosqlite.Connection = Depends(get_db)):
    """브랜드 목록 조회."""
    cursor = await db.execute(
        "SELECT id, name, name_kr, brand_type, website_url, is_active FROM brands WHERE is_active = 1"
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@router.get("/{brand_id}")
async def get_brand(brand_id: str, db: aiosqlite.Connection = Depends(get_db)):
    """브랜드 상세 조회."""
    cursor = await db.execute("SELECT * FROM brands WHERE id = ?", (brand_id,))
    row = await cursor.fetchone()
    if not row:
        return {"error": "Brand not found"}
    return dict(row)


@router.get("/{brand_id}/products")
async def get_brand_products(
    brand_id: str,
    category: Optional[str] = None,
    season: Optional[str] = None,
    db: aiosqlite.Connection = Depends(get_db),
):
    """브랜드별 상품 목록."""
    query = "SELECT * FROM products WHERE brand_id = ? AND is_active = 1"
    params: list = [brand_id]

    if category:
        query += " AND category_id = ?"
        params.append(category)
    if season:
        query += " AND season_id = ?"
        params.append(season)

    query += " ORDER BY created_at DESC"
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]
