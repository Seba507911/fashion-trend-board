"""기존 상품 데이터 컬러 중복 정리 마이그레이션.

같은 (brand_id, product_name, price) 조합의 상품을 하나로 병합하고
컬러와 이미지를 통합한다.

Usage:
    python scripts/dedupe_products.py          # 실행
    python scripts/dedupe_products.py --dry-run # 미리보기만
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "backend" / "db" / "ftib.db"


def merge_json_arrays(existing: str, new: str) -> str:
    """두 JSON 배열 문자열을 병합하고 중복 제거."""
    try:
        a = json.loads(existing) if existing else []
    except (json.JSONDecodeError, TypeError):
        a = []
    try:
        b = json.loads(new) if new else []
    except (json.JSONDecodeError, TypeError):
        b = []
    if not isinstance(a, list):
        a = []
    if not isinstance(b, list):
        b = []
    merged = list(dict.fromkeys(a + b))  # 순서 유지 + 중복 제거
    return json.dumps(merged, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Deduplicate product color variants")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 중복 그룹 찾기
    c.execute("""
        SELECT brand_id, product_name, price, COUNT(*) as cnt
        FROM products
        WHERE is_active = 1
        GROUP BY brand_id, product_name, price
        HAVING cnt > 1
        ORDER BY cnt DESC
    """)
    groups = c.fetchall()

    total_merged = 0
    total_deleted = 0

    for group in groups:
        brand_id = group["brand_id"]
        name = group["product_name"]
        price = group["price"]
        cnt = group["cnt"]

        # 그룹 내 모든 상품 가져오기
        c.execute("""
            SELECT * FROM products
            WHERE brand_id = ? AND product_name = ? AND price = ? AND is_active = 1
            ORDER BY crawled_at DESC
        """, (brand_id, name, price))
        rows = c.fetchall()

        if len(rows) < 2:
            continue

        # 첫 번째(가장 최근 크롤링)를 canonical로 사용
        canonical = dict(rows[0])
        canonical_id = canonical["id"]

        # 나머지에서 컬러, 이미지 병합
        all_colors = canonical.get("colors", "[]")
        all_images = canonical.get("image_urls", "[]")
        all_sizes = canonical.get("sizes", "[]")

        for row in rows[1:]:
            row_dict = dict(row)
            all_colors = merge_json_arrays(all_colors, row_dict.get("colors", "[]"))
            all_images = merge_json_arrays(all_images, row_dict.get("image_urls", "[]"))
            all_sizes = merge_json_arrays(all_sizes, row_dict.get("sizes", "[]"))

        duplicates_to_delete = [dict(r)["id"] for r in rows[1:]]

        if args.dry_run:
            colors = json.loads(all_colors) if all_colors else []
            print(f"  {brand_id:12} | {name[:40]:40} | {cnt} variants → 1 | colors: {len(colors)}")
        else:
            # canonical 행 업데이트
            c.execute("""
                UPDATE products SET colors = ?, image_urls = ?, sizes = ?
                WHERE id = ?
            """, (all_colors, all_images, all_sizes, canonical_id))

            # 나머지 삭제 (soft delete)
            for dup_id in duplicates_to_delete:
                c.execute("DELETE FROM products WHERE id = ?", (dup_id,))

        total_merged += 1
        total_deleted += len(duplicates_to_delete)

    if not args.dry_run:
        conn.commit()

    conn.close()

    print(f"\n--- Summary ---")
    print(f"Groups merged: {total_merged}")
    print(f"Duplicate rows removed: {total_deleted}")
    if args.dry_run:
        print("(dry run — no changes made)")


if __name__ == "__main__":
    main()
