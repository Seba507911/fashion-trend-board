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


@router.get("/vlm-graph")
async def get_vlm_graph_data(
    season: Optional[str] = None,
    db: aiosqlite.Connection = Depends(get_db),
):
    """런웨이 VLM 라벨 기반 그래프 뷰 — 디자이너×컬러×소재×실루엣×텍스처."""
    query = """
        SELECT
            rl.designer, rl.designer_slug,
            vl.dominant_colors, vl.key_materials,
            vl.overall_silhouette, vl.items
        FROM vlm_labels vl
        JOIN runway_looks rl ON rl.id = vl.source_id
    """
    params: list = []
    if season:
        query += " WHERE rl.season = ?"
        params.append(season)

    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()

    nodes: dict = {}
    edges: defaultdict = defaultdict(int)

    # Muted palette per node type
    _designer_palette = [
        "#8B7D6B", "#7A8B6D", "#6B7A8B", "#8B6B7A", "#7D8B6B",
        "#6D7A8B", "#8B7A6B", "#6B8B7D", "#7A6B8B", "#8B6D7A",
    ]
    _type_colors = {
        "material": "#7B97AA",
        "silhouette": "#9E8DBE",
        "texture": "#A0887B",
    }

    designer_counter: Counter = Counter()
    color_counter: Counter = Counter()
    material_counter: Counter = Counter()
    silhouette_counter: Counter = Counter()
    texture_counter: Counter = Counter()

    for row in rows:
        designer = row["designer"]
        designer_slug = row["designer_slug"]
        d_key = f"designer:{designer_slug}"

        designer_counter[designer_slug] += 1

        # 디자이너 노드 (최초 등장 시 등록, 이후 size 업데이트)
        if d_key not in nodes:
            idx = len([n for n in nodes.values() if n["type"] == "designer"]) % len(_designer_palette)
            nodes[d_key] = {
                "id": d_key,
                "label": designer,
                "type": "designer",
                "size": 5,
                "color": _designer_palette[idx],
            }

        # dominant_colors
        colors = _parse_json_field(row["dominant_colors"])
        for c in colors:
            c_lower = c.strip().lower()
            if not c_lower:
                continue
            col_key = f"color:{c_lower}"
            color_counter[c_lower] += 1
            edges[(d_key, col_key)] += 1

        # key_materials
        materials = _parse_json_field(row["key_materials"])
        for m in materials:
            m_clean = m.strip().lower()
            if len(m_clean) < 2:
                continue
            mat_key = f"material:{m_clean}"
            material_counter[m_clean] += 1
            edges[(d_key, mat_key)] += 1
            # color↔material 엣지
            for c in colors:
                c_lower = c.strip().lower()
                if c_lower:
                    edges[(f"color:{c_lower}", mat_key)] += 1

        # overall_silhouette
        sil = row["overall_silhouette"]
        if sil:
            sil_lower = sil.strip().lower()
            sil_key = f"silhouette:{sil_lower}"
            silhouette_counter[sil_lower] += 1
            edges[(d_key, sil_key)] += 1

        # items → textures
        items = _parse_json_field(row["items"])
        for item in items:
            if isinstance(item, dict):
                tex = item.get("texture", "")
                if tex:
                    tex_lower = tex.strip().lower()
                    tex_key = f"texture:{tex_lower}"
                    texture_counter[tex_lower] += 1
                    edges[(d_key, tex_key)] += 1

    # 디자이너 노드 size 업데이트
    for slug, cnt in designer_counter.items():
        d_key = f"designer:{slug}"
        if d_key in nodes:
            nodes[d_key]["size"] = min(5 + cnt // 4, 14)

    # 상위 항목만 노드로 추가
    for col, cnt in color_counter.most_common(20):
        nodes[f"color:{col}"] = {
            "id": f"color:{col}",
            "label": col,
            "type": "color",
            "size": min(3 + cnt // 3, 9),
            "color": _css_color_muted(col),
        }

    for mat, cnt in material_counter.most_common(20):
        nodes[f"material:{mat}"] = {
            "id": f"material:{mat}",
            "label": mat,
            "type": "material",
            "size": min(3 + cnt // 3, 9),
            "color": _type_colors["material"],
        }

    for sil, cnt in silhouette_counter.most_common(10):
        nodes[f"silhouette:{sil}"] = {
            "id": f"silhouette:{sil}",
            "label": sil,
            "type": "silhouette",
            "size": min(4 + cnt // 4, 10),
            "color": _type_colors["silhouette"],
        }

    for tex, cnt in texture_counter.most_common(15):
        nodes[f"texture:{tex}"] = {
            "id": f"texture:{tex}",
            "label": tex,
            "type": "texture",
            "size": min(3 + cnt // 4, 8),
            "color": _type_colors["texture"],
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


@router.get("/vlm-kpi")
async def get_vlm_kpi(db: aiosqlite.Connection = Depends(get_db)):
    """VLM 라벨링 기반 KPI: 총 룩 수, 탑 컬러, 탑 실루엣, 탑 소재."""
    cursor = await db.execute(
        "SELECT vl.dominant_colors, vl.key_materials, vl.overall_silhouette, vl.items "
        "FROM vlm_labels vl"
    )
    rows = await cursor.fetchall()

    total = len(rows)
    color_counter: Counter = Counter()
    material_counter: Counter = Counter()
    silhouette_counter: Counter = Counter()
    texture_counter: Counter = Counter()

    for row in rows:
        for c in _parse_json_field(row["dominant_colors"]):
            color_counter[c.strip().lower()] += 1
        for m in _parse_json_field(row["key_materials"]):
            material_counter[m.strip().lower()] += 1
        sil = row["overall_silhouette"]
        if sil:
            silhouette_counter[sil.strip().lower()] += 1
        for item in _parse_json_field(row["items"]):
            if isinstance(item, dict) and item.get("texture"):
                texture_counter[item["texture"].strip().lower()] += 1

    top_color = color_counter.most_common(1)[0] if color_counter else ("N/A", 0)
    top_material = material_counter.most_common(1)[0] if material_counter else ("N/A", 0)
    top_silhouette = silhouette_counter.most_common(1)[0] if silhouette_counter else ("N/A", 0)
    top_texture = texture_counter.most_common(1)[0] if texture_counter else ("N/A", 0)

    return {
        "total_looks": total,
        "top_color": {"name": top_color[0], "count": top_color[1]},
        "top_material": {"name": top_material[0], "count": top_material[1]},
        "top_silhouette": {"name": top_silhouette[0], "count": top_silhouette[1]},
        "top_texture": {"name": top_texture[0], "count": top_texture[1]},
    }


@router.get("/vlm-colors")
async def get_vlm_color_distribution(db: aiosqlite.Connection = Depends(get_db)):
    """VLM 라벨 기반 컬러 분포 — 전체 + 디자이너별."""
    cursor = await db.execute(
        "SELECT rl.designer_slug, vl.dominant_colors "
        "FROM vlm_labels vl JOIN runway_looks rl ON rl.id = vl.source_id"
    )
    rows = await cursor.fetchall()

    total_colors: Counter = Counter()
    designer_colors: defaultdict = defaultdict(Counter)

    for row in rows:
        colors = _parse_json_field(row["dominant_colors"])
        for c in colors:
            c_lower = c.strip().lower()
            if c_lower:
                total_colors[c_lower] += 1
                designer_colors[row["designer_slug"]][c_lower] += 1

    return {
        "total": [{"color": k, "count": v} for k, v in total_colors.most_common(20)],
        "by_designer": {
            designer: [{"color": k, "count": v} for k, v in counts.most_common(10)]
            for designer, counts in designer_colors.items()
        },
    }


@router.get("/vlm-materials")
async def get_vlm_material_matrix(db: aiosqlite.Connection = Depends(get_db)):
    """VLM 라벨 기반 디자이너 × 소재 매트릭스."""
    cursor = await db.execute(
        "SELECT rl.designer_slug, vl.key_materials "
        "FROM vlm_labels vl JOIN runway_looks rl ON rl.id = vl.source_id"
    )
    rows = await cursor.fetchall()

    designer_materials: defaultdict = defaultdict(Counter)
    all_materials: Counter = Counter()

    for row in rows:
        materials = _parse_json_field(row["key_materials"])
        for m in materials:
            m_clean = m.strip().lower()
            if len(m_clean) > 1:
                designer_materials[row["designer_slug"]][m_clean] += 1
                all_materials[m_clean] += 1

    top_materials = [m for m, _ in all_materials.most_common(15)]

    matrix = []
    for designer, counts in designer_materials.items():
        row_data = {"designer": designer}
        for mat in top_materials:
            row_data[mat] = counts.get(mat, 0)
        matrix.append(row_data)

    return {
        "materials": top_materials,
        "matrix": matrix,
    }


@router.get("/vlm-silhouettes")
async def get_vlm_silhouette_distribution(db: aiosqlite.Connection = Depends(get_db)):
    """VLM 라벨 기반 실루엣 분포 — 전체 + 디자이너별."""
    cursor = await db.execute(
        "SELECT rl.designer_slug, vl.overall_silhouette "
        "FROM vlm_labels vl JOIN runway_looks rl ON rl.id = vl.source_id"
    )
    rows = await cursor.fetchall()

    total_silhouettes: Counter = Counter()
    designer_silhouettes: defaultdict = defaultdict(Counter)

    for row in rows:
        sil = row["overall_silhouette"]
        if sil:
            sil_lower = sil.strip().lower()
            total_silhouettes[sil_lower] += 1
            designer_silhouettes[row["designer_slug"]][sil_lower] += 1

    return {
        "total": [{"silhouette": k, "count": v} for k, v in total_silhouettes.most_common(15)],
        "by_designer": {
            designer: [{"silhouette": k, "count": v} for k, v in counts.most_common(5)]
            for designer, counts in designer_silhouettes.items()
        },
    }


@router.get("/vlm-textures")
async def get_vlm_texture_distribution(db: aiosqlite.Connection = Depends(get_db)):
    """VLM 라벨 기반 텍스처 분포."""
    cursor = await db.execute(
        "SELECT rl.designer_slug, vl.items "
        "FROM vlm_labels vl JOIN runway_looks rl ON rl.id = vl.source_id"
    )
    rows = await cursor.fetchall()

    total_textures: Counter = Counter()
    designer_textures: defaultdict = defaultdict(Counter)

    for row in rows:
        items = _parse_json_field(row["items"])
        for item in items:
            if isinstance(item, dict):
                tex = item.get("texture", "")
                if tex:
                    tex_lower = tex.strip().lower()
                    total_textures[tex_lower] += 1
                    designer_textures[row["designer_slug"]][tex_lower] += 1

    return {
        "total": [{"texture": k, "count": v} for k, v in total_textures.most_common(15)],
        "by_designer": {
            designer: [{"texture": k, "count": v} for k, v in counts.most_common(5)]
            for designer, counts in designer_textures.items()
        },
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
