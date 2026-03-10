"""분석 API 라우터 — Trend Analysis & Graph View 데이터."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Optional

from fastapi import APIRouter, Depends
import aiosqlite

from backend.db.database import get_db

router = APIRouter()


def _parse_json_field(val: Optional[str]) -> list:
    if not val:
        return []
    try:
        parsed = json.loads(val)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def _clean_color(name: str) -> str:
    """NB 등에서 '(19)BLACK' 형태를 'black'으로 정리."""
    import re
    cleaned = re.sub(r"^\(\d+\)", "", name).strip().lower()
    return cleaned if cleaned else name.lower()


@router.get("/kpi")
async def get_kpi(db: aiosqlite.Connection = Depends(get_db)):
    """핵심 KPI: 총 상품 수, 탑 컬러, 트렌딩 핏, 탑 소재."""
    cursor = await db.execute(
        "SELECT colors, materials, fit_info FROM products WHERE is_active = 1"
    )
    rows = await cursor.fetchall()

    total = len(rows)
    color_counter = Counter()
    material_counter = Counter()
    fit_counter = Counter()

    for row in rows:
        for c in _parse_json_field(row["colors"]):
            color_counter[_clean_color(c)] += 1
        for m in _parse_json_field(row["materials"]):
            material_counter[m.strip()] += 1
        fit = row["fit_info"]
        if fit:
            for keyword in ["slim", "regular", "relaxed", "oversized", "crop", "loose", "fitted"]:
                if keyword in fit.lower():
                    fit_counter[keyword] += 1

    top_color = color_counter.most_common(1)[0] if color_counter else ("N/A", 0)
    top_material = material_counter.most_common(1)[0] if material_counter else ("N/A", 0)
    top_fit = fit_counter.most_common(1)[0] if fit_counter else ("N/A", 0)

    return {
        "total_products": total,
        "top_color": {"name": top_color[0], "count": top_color[1]},
        "top_material": {"name": top_material[0], "count": top_material[1]},
        "trending_fit": {"name": top_fit[0], "count": top_fit[1]},
    }


@router.get("/colors")
async def get_color_distribution(db: aiosqlite.Connection = Depends(get_db)):
    """브랜드별 컬러 분포."""
    cursor = await db.execute(
        "SELECT brand_id, colors FROM products WHERE is_active = 1"
    )
    rows = await cursor.fetchall()

    # 전체 컬러 분포
    total_colors = Counter()
    brand_colors = defaultdict(Counter)

    for row in rows:
        colors = _parse_json_field(row["colors"])
        for c in colors:
            c_lower = _clean_color(c)
            total_colors[c_lower] += 1
            brand_colors[row["brand_id"]][c_lower] += 1

    return {
        "total": [{"color": k, "count": v} for k, v in total_colors.most_common(20)],
        "by_brand": {
            brand: [{"color": k, "count": v} for k, v in counts.most_common(10)]
            for brand, counts in brand_colors.items()
        },
    }


@router.get("/materials")
async def get_material_matrix(db: aiosqlite.Connection = Depends(get_db)):
    """브랜드 × 소재 매트릭스."""
    cursor = await db.execute(
        "SELECT brand_id, materials FROM products WHERE is_active = 1"
    )
    rows = await cursor.fetchall()

    brand_materials = defaultdict(Counter)
    all_materials = Counter()

    for row in rows:
        materials = _parse_json_field(row["materials"])
        for m in materials:
            m_clean = m.strip()
            if len(m_clean) > 1:
                brand_materials[row["brand_id"]][m_clean] += 1
                all_materials[m_clean] += 1

    top_materials = [m for m, _ in all_materials.most_common(15)]

    matrix = []
    for brand, counts in brand_materials.items():
        row_data = {"brand": brand}
        for mat in top_materials:
            row_data[mat] = counts.get(mat, 0)
        matrix.append(row_data)

    return {
        "materials": top_materials,
        "matrix": matrix,
    }


@router.get("/categories")
async def get_category_distribution(db: aiosqlite.Connection = Depends(get_db)):
    """브랜드별 카테고리 분포."""
    cursor = await db.execute(
        "SELECT brand_id, category_id, COUNT(*) as cnt "
        "FROM products WHERE is_active = 1 GROUP BY brand_id, category_id"
    )
    rows = await cursor.fetchall()

    result = defaultdict(dict)
    for row in rows:
        result[row["brand_id"]][row["category_id"] or "uncategorized"] = row["cnt"]

    return dict(result)


@router.get("/graph")
async def get_graph_data(db: aiosqlite.Connection = Depends(get_db)):
    """그래프 뷰용 노드 & 엣지 데이터."""
    cursor = await db.execute(
        "SELECT brand_id, category_id, colors, materials FROM products WHERE is_active = 1"
    )
    rows = await cursor.fetchall()

    nodes = {}
    edges = defaultdict(int)

    # Muted warm earth tones for brands — harmonious within the layer
    brand_colors = {
        "alo": "#7BA596", "newbalance": "#B07D6A", "marithe": "#6E8CA0", "asics": "#C4A46C",
        "coor": "#8A9E82", "blankroom": "#7A7A7A", "youth": "#C09566",
        "lemaire": "#A08B7A", "northface": "#B5736A", "descente": "#6B8DAA",
    }

    # 브랜드 노드 수집
    brand_counts = Counter()
    for row in rows:
        brand_counts[row["brand_id"]] += 1

    for brand, count in brand_counts.items():
        nodes[f"brand:{brand}"] = {
            "id": f"brand:{brand}",
            "label": brand,
            "type": "brand",
            "size": min(5 + count // 8, 12),
            "color": brand_colors.get(brand, "#999"),
        }

    # 소재, 컬러, 카테고리 노드 및 엣지
    material_counter = Counter()
    color_counter = Counter()
    category_counter = Counter()

    for row in rows:
        brand_key = f"brand:{row['brand_id']}"
        cat = row["category_id"] or "uncategorized"
        cat_key = f"cat:{cat}"

        category_counter[cat] += 1
        edges[(brand_key, cat_key)] += 1

        for m in _parse_json_field(row["materials"]):
            m_clean = m.strip()
            if len(m_clean) > 1:
                mat_key = f"mat:{m_clean}"
                material_counter[m_clean] += 1
                edges[(brand_key, mat_key)] += 1
                edges[(cat_key, mat_key)] += 1

        for c in _parse_json_field(row["colors"]):
            c_lower = _clean_color(c)
            if c_lower:
                col_key = f"color:{c_lower}"
                color_counter[c_lower] += 1
                edges[(brand_key, col_key)] += 1

    # 상위 항목만 노드로 추가 (너무 많으면 시각화가 복잡해짐)
    for mat, cnt in material_counter.most_common(20):
        nodes[f"mat:{mat}"] = {
            "id": f"mat:{mat}",
            "label": mat,
            "type": "material",
            "size": min(3 + cnt // 5, 9),
            "color": "#7B97AA",
        }

    for col, cnt in color_counter.most_common(15):
        nodes[f"color:{col}"] = {
            "id": f"color:{col}",
            "label": col,
            "type": "color",
            "size": min(3 + cnt // 5, 8),
            "color": _css_color_muted(col),
        }

    for cat, cnt in category_counter.items():
        nodes[f"cat:{cat}"] = {
            "id": f"cat:{cat}",
            "label": cat,
            "type": "category",
            "size": min(4 + cnt // 6, 10),
            "color": "#9E8DBE",
        }

    # 엣지 — 양쪽 노드가 모두 존재하는 것만
    edge_list = []
    for (src, tgt), weight in edges.items():
        if src in nodes and tgt in nodes:
            edge_list.append({"source": src, "target": tgt, "weight": weight})

    return {
        "nodes": list(nodes.values()),
        "edges": edge_list,
    }


def _css_color(name: str) -> str:
    """컬러 이름을 CSS 색상으로 매핑."""
    mapping = {
        "black": "#1a1a1a", "white": "#e0e0e0", "gray": "#888",
        "grey": "#888", "navy": "#1a237e", "blue": "#2196F3",
        "red": "#e53935", "pink": "#EC407A", "green": "#43A047",
        "yellow": "#FDD835", "beige": "#D4C5A9", "brown": "#6D4C41",
        "cream": "#FFFDD0", "olive": "#808000", "charcoal": "#36454F",
        "mint": "#98FF98", "ivory": "#FFFFF0", "khaki": "#C3B091",
        "orange": "#FF9800", "purple": "#9C27B0", "lavender": "#B39DDB",
        "sand": "#C2B280", "camel": "#C19A6B",
    }
    return mapping.get(name, "#78909C")


def _css_color_muted(name: str) -> str:
    """컬러 이름을 차분한(muted) CSS 색상으로 매핑 — 그래프 노드용."""
    mapping = {
        "black": "#5A5A5A", "white": "#C8C8C8", "gray": "#9E9E9E",
        "grey": "#9E9E9E", "navy": "#607088", "blue": "#7BA3C4",
        "red": "#C08080", "pink": "#C89AAA", "green": "#7AAA88",
        "yellow": "#C8B870", "beige": "#C4B89A", "brown": "#967860",
        "cream": "#D4CDB0", "olive": "#8A9060", "charcoal": "#6A7078",
        "mint": "#8AC0A0", "ivory": "#D0CCBA", "khaki": "#B0A480",
        "orange": "#C89870", "purple": "#9A88B0", "lavender": "#A098C0",
        "sand": "#B8AA88", "camel": "#B09478",
    }
    return mapping.get(name, "#90A0A8")
