"""Trend Flow API — 런웨이→셀럽→마켓 트렌드 전파 시각화 데이터."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from typing import Optional

from fastapi import APIRouter, Depends
import aiosqlite

from backend.db.database import get_db

router = APIRouter()


def _parse_json(val: Optional[str]) -> list:
    if not val:
        return []
    try:
        parsed = json.loads(val)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


# ─── 트렌드 키워드 (런웨이 + 마켓 공통) ───

TRACKED_KEYWORDS = [
    {"id": "burgundy", "label": "Burgundy", "group": "color"},
    {"id": "sheer", "label": "Sheer", "group": "material"},
    {"id": "leather", "label": "Leather", "group": "material"},
    {"id": "oversized", "label": "Oversized", "group": "silhouette"},
    {"id": "denim", "label": "Denim", "group": "material"},
    {"id": "navy", "label": "Navy", "group": "color"},
    {"id": "wide_pants", "label": "Wide Pants", "group": "silhouette"},
    {"id": "knit", "label": "Knitwear", "group": "category"},
    {"id": "minimal", "label": "Minimal", "group": "style"},
    {"id": "black", "label": "Black", "group": "color"},
]


@router.get("/keywords")
async def get_tracked_keywords():
    """추적 중인 트렌드 키워드 목록."""
    return TRACKED_KEYWORDS


@router.get("/runway-signals")
async def get_runway_signals(db: aiosqlite.Connection = Depends(get_db)):
    """1단계: 런웨이에서 추출한 트렌드 시그널."""
    cursor = await db.execute(
        "SELECT designer, season, look_number, image_url, tags "
        "FROM runway_looks ORDER BY season DESC"
    )
    rows = await cursor.fetchall()

    tag_counter = Counter()
    designer_tags = defaultdict(Counter)
    season_counts = defaultdict(int)
    total_looks = len(rows)

    for row in rows:
        tags = _parse_json(row["tags"])
        season_counts[row["season"]] += 1
        for tag in tags:
            t = tag.lower().strip()
            tag_counter[t] += 1
            designer_tags[row["designer"]][t] += 1

    top_signals = [
        {"keyword": k, "count": v, "pct": round(v / total_looks * 100, 1) if total_looks else 0}
        for k, v in tag_counter.most_common(20)
    ]

    # 디자이너별 top 키워드
    designer_focus = {}
    for designer, counts in designer_tags.items():
        designer_focus[designer] = [
            {"keyword": k, "count": v}
            for k, v in counts.most_common(5)
        ]

    return {
        "total_looks": total_looks,
        "seasons": dict(season_counts),
        "top_signals": top_signals,
        "designer_focus": designer_focus,
    }


@router.get("/market-validation")
async def get_market_validation(db: aiosqlite.Connection = Depends(get_db)):
    """4단계: 마켓에서의 트렌드 키워드 검증."""
    cursor = await db.execute(
        "SELECT brand_id, product_name, category_id, colors, materials, style_tags, price, sale_price "
        "FROM products WHERE is_active = 1"
    )
    rows = await cursor.fetchall()

    total_products = len(rows)

    # 키워드별 마켓 매칭
    keyword_matches = {}
    for kw in TRACKED_KEYWORDS:
        kid = kw["id"]
        label = kw["label"].lower()
        matched = 0
        brand_dist = Counter()

        for row in rows:
            text_blob = " ".join([
                row["product_name"] or "",
                row["category_id"] or "",
                row["colors"] or "",
                row["materials"] or "",
                row["style_tags"] or "",
            ]).lower()

            if label in text_blob or kid in text_blob:
                matched += 1
                brand_dist[row["brand_id"]] += 1

        keyword_matches[kid] = {
            "keyword": kw["label"],
            "group": kw["group"],
            "matched_products": matched,
            "match_rate": round(matched / total_products * 100, 1) if total_products else 0,
            "by_brand": [{"brand": b, "count": c} for b, c in brand_dist.most_common(10)],
        }

    # 전체 컬러 트렌드 (마켓)
    color_counter = Counter()
    for row in rows:
        for c in _parse_json(row["colors"]):
            c_clean = re.sub(r"^\(\d+\)", "", c).strip().lower()
            if c_clean:
                color_counter[c_clean] += 1

    # 카테고리 분포
    cat_counter = Counter()
    for row in rows:
        if row["category_id"]:
            cat_counter[row["category_id"]] += 1

    # 할인율 분포 (트렌드 인기 지표)
    discount_brands = defaultdict(list)
    for row in rows:
        if row["price"] and row["sale_price"] and row["price"] > 0:
            disc = round((1 - row["sale_price"] / row["price"]) * 100, 1)
            if disc > 0:
                discount_brands[row["brand_id"]].append(disc)

    avg_discounts = {
        brand: round(sum(discs) / len(discs), 1)
        for brand, discs in discount_brands.items()
        if discs
    }

    return {
        "total_products": total_products,
        "keyword_matches": keyword_matches,
        "top_colors": [{"color": k, "count": v} for k, v in color_counter.most_common(15)],
        "categories": [{"category": k, "count": v} for k, v in cat_counter.most_common()],
        "avg_discounts": avg_discounts,
    }


@router.get("/celeb-mock")
async def get_celeb_mock():
    """3단계: 셀럽/인플루언서 목업 데이터."""
    return {
        "groups": [
            {
                "id": "global_celeb",
                "label": "Global Celebrity",
                "people": [
                    {"name": "Zendaya", "tags": ["burgundy", "sheer", "oversized"], "looks": 12, "trend_match": 85},
                    {"name": "Hailey Bieber", "tags": ["minimal", "leather", "black"], "looks": 18, "trend_match": 78},
                    {"name": "Bella Hadid", "tags": ["denim", "vintage", "oversized"], "looks": 15, "trend_match": 72},
                    {"name": "Rosé", "tags": ["black", "leather", "minimal"], "looks": 9, "trend_match": 90},
                ],
            },
            {
                "id": "kr_celeb",
                "label": "Korean Celebrity",
                "people": [
                    {"name": "김고은", "tags": ["minimal", "knit", "navy"], "looks": 8, "trend_match": 82},
                    {"name": "수지", "tags": ["leather", "black", "oversized"], "looks": 11, "trend_match": 75},
                    {"name": "아이유", "tags": ["sheer", "burgundy", "dress"], "looks": 7, "trend_match": 88},
                    {"name": "제니", "tags": ["leather", "black", "denim"], "looks": 14, "trend_match": 92},
                ],
            },
            {
                "id": "global_influencer",
                "label": "Global Influencer",
                "people": [
                    {"name": "Chiara Ferragni", "tags": ["oversized", "denim", "leather"], "looks": 22, "trend_match": 68},
                    {"name": "Aimee Song", "tags": ["minimal", "knit", "wide_pants"], "looks": 16, "trend_match": 74},
                    {"name": "Leonie Hanne", "tags": ["sheer", "burgundy", "leather"], "looks": 19, "trend_match": 80},
                ],
            },
            {
                "id": "kr_influencer",
                "label": "Korean Influencer",
                "people": [
                    {"name": "한혜연", "tags": ["oversized", "navy", "minimal"], "looks": 14, "trend_match": 86},
                    {"name": "이사배", "tags": ["black", "leather", "denim"], "looks": 10, "trend_match": 70},
                    {"name": "김나영", "tags": ["knit", "wide_pants", "minimal"], "looks": 12, "trend_match": 78},
                ],
            },
        ],
    }


@router.get("/expert-mock")
async def get_expert_mock():
    """2단계: 전문가 리포트 목업 데이터."""
    return {
        "reports": [
            {
                "id": "wgsn_fw26",
                "source": "WGSN",
                "title": "FW26 Key Color Direction",
                "date": "2025-12",
                "predictions": [
                    {"keyword": "burgundy", "confidence": "high", "runway_match": True},
                    {"keyword": "navy", "confidence": "high", "runway_match": True},
                    {"keyword": "forest green", "confidence": "medium", "runway_match": False},
                    {"keyword": "sheer", "confidence": "high", "runway_match": True},
                ],
            },
            {
                "id": "pantone_fw26",
                "source": "Pantone",
                "title": "FW26 Color of the Year Impact",
                "date": "2025-11",
                "predictions": [
                    {"keyword": "mocha mousse", "confidence": "high", "runway_match": False},
                    {"keyword": "burgundy", "confidence": "medium", "runway_match": True},
                    {"keyword": "black", "confidence": "high", "runway_match": True},
                ],
            },
            {
                "id": "edited_fw26",
                "source": "EDITED",
                "title": "FW26 Material & Silhouette Forecast",
                "date": "2026-01",
                "predictions": [
                    {"keyword": "leather", "confidence": "high", "runway_match": True},
                    {"keyword": "oversized", "confidence": "high", "runway_match": True},
                    {"keyword": "wide_pants", "confidence": "medium", "runway_match": True},
                    {"keyword": "denim", "confidence": "medium", "runway_match": True},
                    {"keyword": "knit", "confidence": "low", "runway_match": True},
                ],
            },
        ],
    }


@router.get("/forecast-mock")
async def get_forecast_mock():
    """5단계: 넥스트 런웨이 예측 목업 데이터."""
    return {
        "expanding": [
            {"keyword": "Burgundy", "signal": "셀럽 착용 ↑42%, 마켓 등장 ↑28%", "confidence": 88},
            {"keyword": "Leather", "signal": "전 브랜드 확대, 검색량 ↑65%", "confidence": 92},
            {"keyword": "Oversized", "signal": "인플루언서 착용 1위, 런웨이 지속", "confidence": 85},
        ],
        "shrinking": [
            {"keyword": "Crop Top", "signal": "셀럽 착용 ↓30%, 마켓 할인 증가", "confidence": 72},
            {"keyword": "Neon", "signal": "런웨이 등장 ↓60%, SNS 언급 ↓45%", "confidence": 78},
        ],
        "morphing": [
            {"keyword": "Sheer → Layered Sheer", "signal": "단독→레이어드로 변형, 셀럽 스타일링 변화", "confidence": 75},
            {"keyword": "Wide Pants → Barrel Leg", "signal": "실루엣 변형, 디자이너 3곳 채택", "confidence": 68},
            {"keyword": "Denim → Washed Denim", "signal": "워싱 가공 비율 ↑, 인플루언서 트렌드", "confidence": 70},
        ],
    }
