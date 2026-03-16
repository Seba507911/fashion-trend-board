"""Trend Flow Check API — VLM 라벨 + 마켓 실데이터 기반 키워드 대시보드."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, Query
import aiosqlite

from backend.db.database import get_db

router = APIRouter()

# ─── Season format mapping ───

SEASON_MAP = {
    "24SS": "spring-summer-2024",
    "24FW": "fall-winter-2024",
    "25SS": "spring-summer-2025",
    "25FW": "fall-winter-2025",
    "26SS": "spring-summer-2026",
    "26FW": "fall-winter-2026",
}

SEASON_REVERSE = {v: k for k, v in SEASON_MAP.items()}

# ─── Synonym map for market matching ───

SYNONYM_MAP = {
    "burgundy": ["wine", "maroon"],
    "navy": ["dark blue"],
    "cream": ["ivory", "off-white"],
    "camel": ["tan", "beige"],
    "sheer": ["transparent", "see-through"],
    "oversized": ["loose fit", "relaxed fit", "boxy"],
    "leather": ["faux leather", "vegan leather"],
    "denim": ["jeans"],
    "knit": ["knitwear", "knitted"],
    "suede": ["nubuck"],
    "wide": ["wide leg", "wide-leg"],
    "slim": ["skinny", "fitted"],
}

# ─── Category classification from VLM fields ───

CATEGORY_SOURCES = {
    "color": "dominant_colors",
    "material": "key_materials",
    "silhouette": "overall_silhouette",
    "item": "items",
}

# Filter out overly generic keywords
STOP_WORDS = {
    "medium", "small", "large", "mini", "oversized_size",
    "structured", "unstructured",  # too generic silhouettes
    "matte", "glossy", "smooth", "textured",  # textures, not keywords
}


def _parse_json(val: Optional[str]) -> list:
    if not val:
        return []
    try:
        parsed = json.loads(val)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def _normalize(s: str) -> str:
    return s.strip().lower().replace("-", " ").replace("_", " ")


def _extract_keywords_from_vlm(rows: list[aiosqlite.Row]) -> dict[str, Counter]:
    """Extract keywords by category from VLM label rows."""
    by_category: dict[str, Counter] = {
        "color": Counter(),
        "material": Counter(),
        "silhouette": Counter(),
        "item": Counter(),
    }

    for row in rows:
        # Colors
        for c in _parse_json(row["dominant_colors"]):
            kw = _normalize(c)
            if kw and kw not in STOP_WORDS and len(kw) > 1:
                by_category["color"][kw] += 1

        # Materials
        for m in _parse_json(row["key_materials"]):
            kw = _normalize(m)
            if kw and kw not in STOP_WORDS and len(kw) > 1:
                by_category["material"][kw] += 1

        # Silhouette
        sil = row["overall_silhouette"]
        if sil:
            kw = _normalize(sil)
            if kw and kw not in STOP_WORDS and len(kw) > 1:
                by_category["silhouette"][kw] += 1

        # Items
        for item_obj in _parse_json(row["items"]):
            if isinstance(item_obj, dict):
                item_name = item_obj.get("item", "")
                kw = _normalize(item_name)
                if kw and kw not in STOP_WORDS and len(kw) > 1:
                    by_category["item"][kw] += 1

    return by_category


def _match_keyword_in_product(keyword: str, product_text: str) -> bool:
    """Check if keyword or its synonyms appear in product text."""
    kw = _normalize(keyword)
    if kw in product_text:
        return True
    for syn in SYNONYM_MAP.get(kw, []):
        if _normalize(syn) in product_text:
            return True
    return False


def _build_product_text(row: aiosqlite.Row) -> str:
    """Build searchable text blob from product row."""
    parts = [
        row["product_name"] or "",
        row["colors"] or "",
        row["materials"] or "",
        row["style_tags"] or "",
        row["category_id"] or "",
    ]
    return " ".join(parts).lower()


# ─── Mock signals for expert / celeb / search ───

_MOCK_EXPERT = {
    "burgundy": 0.8, "navy": 0.7, "black": 0.9, "cream": 0.5,
    "leather": 0.75, "denim": 0.6, "knit": 0.5, "cotton": 0.3,
    "wool": 0.65, "silk": 0.55, "lace": 0.4, "suede": 0.35,
    "oversized": 0.7, "fitted": 0.5, "relaxed": 0.45, "slim": 0.3,
    "pants": 0.4, "jacket": 0.6, "top": 0.3, "coat": 0.7,
    "dress": 0.55, "skirt": 0.45, "bag": 0.5, "shoe": 0.4,
    "boots": 0.55, "sneakers": 0.35,
}

_MOCK_CELEB = {
    "burgundy": 0.45, "black": 0.7, "white": 0.5, "navy": 0.3,
    "leather": 0.6, "denim": 0.55, "silk": 0.35,
    "oversized": 0.5, "fitted": 0.4, "slim": 0.35,
    "bag": 0.6, "boots": 0.45, "jacket": 0.5, "coat": 0.55,
    "dress": 0.5, "sneakers": 0.4,
}

_MOCK_SEARCH = {
    "burgundy": 0.65, "black": 0.8, "white": 0.6, "navy": 0.4,
    "leather": 0.55, "denim": 0.7, "knit": 0.45, "cotton": 0.35,
    "oversized": 0.6, "wide": 0.5, "slim": 0.55,
    "pants": 0.65, "jacket": 0.55, "bag": 0.5, "sneakers": 0.7,
    "boots": 0.5, "dress": 0.45, "coat": 0.6,
}


@router.get("/keywords")
async def get_keywords(
    season: str = Query(default="26SS", description="시즌 코드 (예: 26SS)"),
    category: Optional[str] = Query(default=None, description="카테고리 필터 (color/material/silhouette/item)"),
    zoning: Optional[str] = Query(default=None, description="조닝 필터"),
    limit: int = Query(default=30, le=50),
    db: aiosqlite.Connection = Depends(get_db),
):
    """VLM 라벨 + 마켓 매칭 기반 트렌드 키워드 목록."""

    db_season = SEASON_MAP.get(season, "spring-summer-2026")

    # 1) VLM 라벨에서 키워드 추출
    cursor = await db.execute(
        """
        SELECT v.dominant_colors, v.key_materials, v.overall_silhouette, v.items,
               r.designer, r.designer_slug, r.season
        FROM vlm_labels v
        JOIN runway_looks r ON v.source_id = r.id
        WHERE r.season = ?
        """,
        (db_season,),
    )
    vlm_rows = await cursor.fetchall()
    total_vlm_looks = len(vlm_rows)

    if total_vlm_looks == 0:
        return {"keywords": [], "total_vlm_looks": 0, "season": season}

    by_category = _extract_keywords_from_vlm(vlm_rows)

    # Keyword → set of designers (for runway_designer_count)
    kw_designers: dict[str, set] = defaultdict(set)
    for row in vlm_rows:
        designer = row["designer"]
        for c in _parse_json(row["dominant_colors"]):
            kw_designers[_normalize(c)].add(designer)
        for m in _parse_json(row["key_materials"]):
            kw_designers[_normalize(m)].add(designer)
        sil = row["overall_silhouette"]
        if sil:
            kw_designers[_normalize(sil)].add(designer)
        for item_obj in _parse_json(row["items"]):
            if isinstance(item_obj, dict):
                kw_designers[_normalize(item_obj.get("item", ""))].add(designer)

    # 2) Gather products for market matching
    prod_cursor = await db.execute(
        "SELECT brand_id, product_name, category_id, colors, materials, style_tags "
        "FROM products WHERE is_active = 1"
    )
    products = await prod_cursor.fetchall()
    total_products = len(products)

    # Pre-build product text blobs
    product_blobs = [(_build_product_text(p), p["brand_id"]) for p in products]

    # 3) Build keyword list
    categories_to_process = (
        [category] if category and category in by_category
        else list(by_category.keys())
    )

    all_keywords = []
    for cat in categories_to_process:
        for kw, runway_count in by_category[cat].most_common(limit):
            # Runway strength: normalized by total looks
            runway_strength = min(1.0, runway_count / (total_vlm_looks * 0.15))
            designer_count = len(kw_designers.get(kw, set()))

            # Market matching
            matched_products = 0
            brand_dist: Counter = Counter()
            for blob, brand_id in product_blobs:
                if _match_keyword_in_product(kw, blob):
                    matched_products += 1
                    brand_dist[brand_id] += 1

            market_strength = min(1.0, matched_products / max(total_products * 0.05, 1))

            # Mock signals
            expert_strength = _MOCK_EXPERT.get(kw, 0.2)
            celeb_strength = _MOCK_CELEB.get(kw, 0.15)
            search_strength = _MOCK_SEARCH.get(kw, 0.25)

            # Confidence
            confidence = round(
                (runway_strength * 0.25
                 + expert_strength * 0.20
                 + celeb_strength * 0.15
                 + search_strength * 0.20
                 + market_strength * 0.20)
                * 100
            )

            brands = [
                {"brand": b, "count": c}
                for b, c in brand_dist.most_common(10)
            ]

            all_keywords.append({
                "keyword": kw,
                "category": cat,
                "confidence": min(confidence, 100),
                "pool": "A" if runway_strength >= 0.3 and expert_strength >= 0.4 else "B",
                "origin": _classify_origin(runway_strength, market_strength, celeb_strength),
                "signals": {
                    "runway": round(runway_strength, 2),
                    "expert": round(expert_strength, 2),
                    "celeb": round(celeb_strength, 2),
                    "search": round(search_strength, 2),
                    "market": round(market_strength, 2),
                },
                "signal_details": {
                    "runway": f"{runway_count}회 · {designer_count} 디자이너",
                    "expert": "WGSN/Pantone (mock)" if expert_strength >= 0.5 else "— (mock)",
                    "celeb": f"착용 {int(celeb_strength * 10)}건 (mock)",
                    "search": f"+{int(search_strength * 100)}% (mock)",
                    "market": f"{matched_products}개 상품",
                },
                "runway_count": runway_count,
                "runway_designers": designer_count,
                "market_count": matched_products,
                "brands": brands,
            })

    # Sort by confidence descending, take top N
    all_keywords.sort(key=lambda x: x["confidence"], reverse=True)
    all_keywords = all_keywords[:limit]

    # Assign IDs
    for i, kw in enumerate(all_keywords):
        kw["id"] = i + 1

    return {
        "keywords": all_keywords,
        "total_vlm_looks": total_vlm_looks,
        "total_products": total_products,
        "season": season,
    }


def _classify_origin(runway: float, market: float, celeb: float) -> str:
    if runway >= 0.4 and market >= 0.3:
        return "runway_led"
    if celeb >= 0.4 and runway < 0.3:
        return "capital_driven"
    if market >= 0.5 and runway < 0.3:
        return "market_organic"
    if celeb >= 0.5 and runway < 0.2:
        return "viral_meme"
    return "unknown"


@router.get("/keyword/{keyword}/detail")
async def get_keyword_detail(
    keyword: str,
    season: str = Query(default="26SS"),
    db: aiosqlite.Connection = Depends(get_db),
):
    """키워드 상세: 시즌별 추이 + 런웨이 디자이너 + 마켓 브랜드 분포."""

    kw = _normalize(keyword)

    # 1) All seasons — runway appearances via VLM
    timeline = []
    for season_code, db_season in SEASON_MAP.items():
        cursor = await db.execute(
            """
            SELECT v.dominant_colors, v.key_materials, v.overall_silhouette, v.items,
                   r.designer
            FROM vlm_labels v
            JOIN runway_looks r ON v.source_id = r.id
            WHERE r.season = ?
            """,
            (db_season,),
        )
        rows = await cursor.fetchall()
        count = 0
        designers: set = set()
        for row in rows:
            found = False
            for c in _parse_json(row["dominant_colors"]):
                if _normalize(c) == kw:
                    found = True
            for m in _parse_json(row["key_materials"]):
                if _normalize(m) == kw:
                    found = True
            sil = row["overall_silhouette"]
            if sil and _normalize(sil) == kw:
                found = True
            for item_obj in _parse_json(row["items"]):
                if isinstance(item_obj, dict) and _normalize(item_obj.get("item", "")) == kw:
                    found = True
            if found:
                count += 1
                designers.add(row["designer"])

        if count > 0:
            timeline.append({
                "season": season_code,
                "runway_count": count,
                "designer_count": len(designers),
                "designers": sorted(designers),
            })

    # 2) Market brand distribution
    prod_cursor = await db.execute(
        "SELECT brand_id, product_name, colors, materials, style_tags, category_id "
        "FROM products WHERE is_active = 1"
    )
    products = await prod_cursor.fetchall()

    brand_dist: Counter = Counter()
    matched_products = []
    for p in products:
        blob = _build_product_text(p)
        if _match_keyword_in_product(kw, blob):
            brand_dist[p["brand_id"]] += 1
            if len(matched_products) < 20:
                matched_products.append({
                    "brand": p["brand_id"],
                    "name": p["product_name"],
                    "category": p["category_id"],
                })

    brands = [{"brand": b, "count": c} for b, c in brand_dist.most_common(15)]

    return {
        "keyword": kw,
        "timeline": timeline,
        "brands": brands,
        "total_market_matches": sum(brand_dist.values()),
        "sample_products": matched_products,
    }
