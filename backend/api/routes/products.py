"""상품 API 라우터."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
import aiosqlite

from backend.db.database import get_db

router = APIRouter()


@router.get("")
async def list_products(
    brand: Optional[str] = None,
    category: Optional[str] = None,
    season: Optional[str] = None,
    keyword: Optional[str] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    limit: int = Query(default=200, le=500),
    offset: int = 0,
    db: aiosqlite.Connection = Depends(get_db),
):
    """상품 목록 (필터링 지원)."""
    query = "SELECT * FROM products WHERE is_active = 1"
    params: list = []

    if brand:
        query += " AND brand_id = ?"
        params.append(brand)
    if category:
        query += " AND category_id = ?"
        params.append(category)
    if season:
        query += " AND season_id = ?"
        params.append(season)
    if keyword:
        like = f"%{keyword}%"
        query += " AND (name LIKE ? OR color LIKE ? OR material LIKE ?)"
        params.extend([like, like, like])
    if price_min is not None:
        query += " AND price >= ?"
        params.append(price_min)
    if price_max is not None:
        query += " AND price <= ?"
        params.append(price_max)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@router.get("/categories")
async def list_categories(db: aiosqlite.Connection = Depends(get_db)):
    """카테고리 목록 (계층형)."""
    cursor = await db.execute(
        "SELECT id, name, name_kr, parent_id, sort_order FROM categories ORDER BY sort_order"
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@router.get("/{product_id}")
async def get_product(product_id: str, db: aiosqlite.Connection = Depends(get_db)):
    """상품 상세."""
    cursor = await db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = await cursor.fetchone()
    if not row:
        return {"error": "Product not found"}
    return dict(row)
