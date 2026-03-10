"""Cafe24 브랜드 컬러-in-이름 중복 정리.

마리떼: "CLASSIC LOGO TEE black" → base="CLASSIC LOGO TEE", color="black"
쿠어: "팬츠 (프렌치블루)" → base="팬츠", color="프렌치블루"
블랭크룸: "JACKET_BLACK CHOCOLATE" → base="JACKET", color="BLACK CHOCOLATE"

Usage:
    python scripts/dedupe_cafe24_colors.py --dry-run
    python scripts/dedupe_cafe24_colors.py
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "backend" / "db" / "ftib.db"

# 영문 컬러 키워드 (긴 것부터 매칭)
EN_COLORS = sorted([
    "light heather gray", "light heather grey", "heather gray", "heather grey",
    "deep navy", "dark navy", "light grey", "light gray", "dark gray", "dark grey",
    "melange gray", "melange grey", "sky blue", "dusty pink", "off white",
    "black chocolate", "midnight brown",
    "black", "white", "navy", "gray", "grey", "cream", "beige", "brown", "blue",
    "red", "green", "pink", "yellow", "orange", "purple", "khaki", "ivory",
    "charcoal", "olive", "mint", "lavender", "sand", "camel", "oatmeal",
    "burgundy", "wine", "coral", "peach", "sage", "taupe", "mocha", "espresso",
    "denim", "indigo", "mauve", "rose", "ecru", "natural", "teal", "cobalt",
    "lime", "stone",
], key=len, reverse=True)

# 한글 컬러 키워드
KR_COLORS = sorted([
    "프렌치블루", "딥블루그레이", "블루그레이", "다크브라운", "딥네이비",
    "다크그레이", "라이트그레이", "라이트베이지", "웜베이지", "올리브카키",
    "베이지", "블랙", "네이비", "브라운", "그레이", "화이트", "아이보리",
    "카키", "올리브", "차콜", "크림", "와인", "버건디", "핑크", "레드",
    "블루", "그린", "옐로우", "오렌지", "퍼플", "민트", "라벤더",
    "카멜", "모카", "샌드", "오트밀", "인디고", "데님", "코발트",
], key=len, reverse=True)


def strip_marithe_color(name: str) -> tuple[str, str]:
    """마리떼: 영문 컬러 suffix 제거."""
    lower = name.lower().strip()
    for cw in EN_COLORS:
        if lower.endswith(" " + cw):
            base = name[: len(name) - len(cw)].strip()
            color = name[len(base):].strip()
            return base, color
    return name, ""


def strip_coor_color(name: str) -> tuple[str, str]:
    """쿠어: (컬러명) 괄호 패턴 제거."""
    m = re.search(r"\s*\(([^)]+)\)\s*$", name)
    if m:
        color_candidate = m.group(1).strip()
        # 한글 컬러인지 확인
        for kc in KR_COLORS:
            if kc in color_candidate:
                base = name[: m.start()].strip()
                return base, color_candidate
        # 영문 컬러
        for ec in EN_COLORS:
            if ec in color_candidate.lower():
                base = name[: m.start()].strip()
                return base, color_candidate
    return name, ""


def strip_blankroom_color(name: str) -> tuple[str, str]:
    """블랭크룸: _COLOR 언더스코어 패턴 제거."""
    if "_" in name:
        base, color = name.rsplit("_", 1)
        color = color.strip()
        if not color:
            return name, ""
        # 컬러 부분이 실제 컬러인지 체크
        color_lower = color.lower()
        for ec in EN_COLORS:
            if ec in color_lower or color_lower in ec:
                return base.strip(), color
        # 2단어 이하이고, 카테고리명이 아니면 컬러로 간주
        category_words = {"pants", "shirt", "skirt", "bag", "belt", "coat",
                          "jacket", "blouson", "knit", "top", "neck", "scarf",
                          "sleeveless", "flare", "jumper", "vest"}
        first_word = color_lower.split()[0] if color.split() else ""
        if first_word not in category_words and len(color.split()) <= 3:
            return base.strip(), color
    return name, ""


def merge_json(a: str, b: list) -> str:
    try:
        existing = json.loads(a) if a else []
    except (json.JSONDecodeError, TypeError):
        existing = []
    if not isinstance(existing, list):
        existing = []
    merged = list(dict.fromkeys(existing + b))
    return json.dumps(merged, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    brand_strippers = {
        "marithe": strip_marithe_color,
        "coor": strip_coor_color,
        "blankroom": strip_blankroom_color,
    }

    total_merged = 0
    total_deleted = 0

    for brand_id, strip_fn in brand_strippers.items():
        c.execute(
            "SELECT * FROM products WHERE brand_id=? AND is_active=1 ORDER BY product_name",
            (brand_id,),
        )
        rows = [dict(r) for r in c.fetchall()]

        # base_name + price 로 그룹핑
        groups: dict[tuple, list] = defaultdict(list)
        for row in rows:
            base, color = strip_fn(row["product_name"])
            row["_base_name"] = base
            row["_extracted_color"] = color
            groups[(base, row["price"])].append(row)

        brand_merged = 0
        brand_deleted = 0

        for (base_name, price), items in groups.items():
            if len(items) < 2:
                # 단일 상품이라도 이름에서 컬러 제거 + colors에 추가
                item = items[0]
                if item["_extracted_color"]:
                    new_colors = merge_json(item["colors"], [item["_extracted_color"]])
                    if not args.dry_run:
                        c.execute(
                            "UPDATE products SET product_name=?, product_name_kr=?, colors=? WHERE id=?",
                            (base_name, base_name, new_colors, item["id"]),
                        )
                continue

            # 여러 컬러 변형 → 병합
            canonical = items[0]
            all_colors = []
            all_images = canonical.get("image_urls", "[]")

            for item in items:
                if item["_extracted_color"]:
                    all_colors.append(item["_extracted_color"])
                # 기존 colors 배열도 병합
                try:
                    existing = json.loads(item.get("colors", "[]") or "[]")
                    all_colors.extend(existing if isinstance(existing, list) else [])
                except (json.JSONDecodeError, TypeError):
                    pass
                all_images = merge_json(all_images, [])
                try:
                    imgs = json.loads(item.get("image_urls", "[]") or "[]")
                    all_images = merge_json(all_images, imgs if isinstance(imgs, list) else [])
                except (json.JSONDecodeError, TypeError):
                    pass

            # 노이즈 컬러 제거 (PANTS_BROWN 같은 관련상품 참조)
            noise_prefixes = ("pants_", "shirt_", "skirt_", "bag_", "belt_", "coat_",
                              "jacket_", "blouson_", "knit_", "top_", "neck_", "scarf_",
                              "sleeveless_", "flare_", "jumper_", "vest_")
            clean_colors = [c for c in all_colors
                            if not c.lower().startswith(noise_prefixes)]
            unique_colors = list(dict.fromkeys(clean_colors))
            colors_json = json.dumps(unique_colors, ensure_ascii=False)

            if args.dry_run:
                print(
                    f"  {brand_id:12} | {len(items):2} → 1 | {base_name[:45]:45} | colors: {unique_colors}"
                )
            else:
                # canonical 업데이트
                c.execute(
                    "UPDATE products SET product_name=?, product_name_kr=?, colors=?, image_urls=? WHERE id=?",
                    (base_name, base_name, colors_json, all_images, canonical["id"]),
                )
                # 나머지 삭제
                for item in items[1:]:
                    c.execute("DELETE FROM products WHERE id=?", (item["id"],))

            brand_merged += 1
            brand_deleted += len(items) - 1

        print(f"{brand_id}: merged {brand_merged} groups, deleted {brand_deleted} rows")
        total_merged += brand_merged
        total_deleted += brand_deleted

    if not args.dry_run:
        conn.commit()

    conn.close()
    print(f"\n--- Total: merged {total_merged} groups, deleted {total_deleted} rows ---")
    if args.dry_run:
        print("(dry run)")


if __name__ == "__main__":
    main()
