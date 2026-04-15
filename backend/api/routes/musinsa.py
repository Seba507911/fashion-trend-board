"""무신사 상품 API 라우트."""
from __future__ import annotations

from typing import Optional

import aiosqlite
from fastapi import APIRouter, Depends, Query

from backend.db.database import get_db

router = APIRouter(prefix="/musinsa", tags=["musinsa"])


@router.get("/brands")
async def get_brands(db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute(
        "SELECT brand_slug, brand_name, COUNT(*) as cnt FROM musinsa_products GROUP BY brand_slug, brand_name ORDER BY cnt DESC"
    )
    return [dict(r) for r in await rows.fetchall()]


@router.get("/zonings")
async def get_zonings(db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute(
        "SELECT zoning, COUNT(DISTINCT brand_slug) as brands, COUNT(*) as products FROM musinsa_products WHERE zoning IS NOT NULL GROUP BY zoning ORDER BY products DESC"
    )
    return [dict(r) for r in await rows.fetchall()]


@router.get("/products")
async def get_products(
    brand_slug: Optional[str] = None,
    zoning: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=200, le=1000),
    db: aiosqlite.Connection = Depends(get_db),
):
    q = "SELECT * FROM musinsa_products WHERE 1=1"
    params = []
    if brand_slug:
        q += " AND brand_slug = ?"
        params.append(brand_slug)
    if zoning:
        q += " AND zoning = ?"
        params.append(zoning)
    if search:
        q += " AND UPPER(product_name) LIKE ?"
        params.append(f"%{search.upper()}%")
    q += f" ORDER BY brand_name, product_name LIMIT {limit}"
    rows = await db.execute(q, params)
    return [dict(r) for r in await rows.fetchall()]


@router.get("/stats")
async def get_stats(db: aiosqlite.Connection = Depends(get_db)):
    brands = await (await db.execute("SELECT COUNT(DISTINCT brand_slug) FROM musinsa_products")).fetchone()
    products = await (await db.execute("SELECT COUNT(*) FROM musinsa_products")).fetchone()
    return {"total_brands": brands[0], "total_products": products[0]}
