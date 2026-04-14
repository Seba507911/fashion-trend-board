"""Snowflake 무신사 키워드 트렌드 분석.

무신사 주간 랭킹 데이터에서 런웨이 키워드의 마켓 침투율을 추적한다.
상품명 텍스트 매칭 + 카테고리 필터로 노이즈 제거.

Usage:
    python scripts/snowflake_keyword_trend.py
    python scripts/snowflake_keyword_trend.py --keyword 레이스
    python scripts/snowflake_keyword_trend.py --list-products 가죽 --limit 30
"""
from __future__ import annotations

import argparse
import os
from dotenv import load_dotenv
import snowflake.connector


# ── 키워드 정의: 검색 패턴 + 노이즈 제거 규칙 ──

KEYWORDS = {
    "가죽/레더": {
        "include": ["가죽", "레더", "LEATHER"],
        "exclude_name": [],
        "include_category": ["아우터", "상의", "바지", "원피스/스커트", "가방"],
        "exclude_mid": [],
    },
    "시어/시스루": {
        "include": ["시어", "시스루", "SHEER"],
        "exclude_name": ["시어셸", "시어쉘", "SHEER SHELL"],
        "include_category": ["상의", "원피스/스커트", "바지", "아우터"],
        "exclude_mid": ["나일론/코치 재킷", "아노락 재킷", "숏패딩/숏헤비 아우터", "무스탕/퍼"],
    },
    "레이스": {
        "include": ["레이스", "LACE"],
        "exclude_name": ["레이스업", "LACE UP", "LACE-UP"],
        "include_category": ["상의", "원피스/스커트", "바지", "아우터"],
        "exclude_mid": [],
    },
    "크롭": {
        "include": ["크롭", "CROP"],
        "exclude_name": [],
        "include_category": ["상의", "아우터", "원피스/스커트"],
        "exclude_mid": [],
    },
    "오버사이즈": {
        "include": ["오버사이즈", "오버핏", "OVERSIZE", "OVERFIT"],
        "exclude_name": [],
        "include_category": ["상의", "아우터", "바지", "원피스/스커트"],
        "exclude_mid": [],
    },
    "러플": {
        "include": ["러플", "프릴", "RUFFLE", "FRILL"],
        "exclude_name": [],
        "include_category": ["상의", "원피스/스커트", "바지"],
        "exclude_mid": [],
    },
    "워크웨어": {
        "include": ["워크웨어", "카고", "유틸리티", "CARGO", "UTILITY", "WORKWEAR"],
        "exclude_name": [],
        "include_category": ["상의", "아우터", "바지"],
        "exclude_mid": [],
    },
}


def get_connection():
    load_dotenv()
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        authenticator="externalbrowser",
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )


def build_where(kw_config: dict) -> str:
    """키워드 config로부터 WHERE 절을 생성."""
    # include patterns
    likes = " OR ".join(
        [f"UPPER(PRODUCT_NAME) LIKE '%{p.upper()}%'" for p in kw_config["include"]]
    )
    where = f"({likes})"

    # exclude name patterns
    for ex in kw_config.get("exclude_name", []):
        where += f" AND UPPER(PRODUCT_NAME) NOT LIKE '%{ex.upper()}%'"

    # include categories
    cats = kw_config.get("include_category", [])
    if cats:
        cat_list = ",".join([f"'{c}'" for c in cats])
        where += f" AND MAIN_CATEGORY IN ({cat_list})"

    # exclude mid categories
    for mid in kw_config.get("exclude_mid", []):
        where += f" AND MID_CATEGORY != '{mid}'"

    return where


def trend_query(kw_name: str, start_date: str = "2025-01-01"):
    """분기별 트렌드 출력."""
    conn = get_connection()
    cur = conn.cursor()

    config = KEYWORDS[kw_name]
    where = build_where(config)

    sql = f"""
        SELECT DATE_TRUNC('WEEK', UPDATE_DATE)::DATE as week,
               COUNT(DISTINCT PRODUCT_CODE) as products,
               COUNT(DISTINCT BRAND) as brands
        FROM DW_MUSINSA_PRDT_RNK_W
        WHERE UPDATE_DATE >= '{start_date}' AND {where}
        GROUP BY week
        ORDER BY week
    """
    cur.execute(sql)
    rows = cur.fetchall()

    print(f"\n=== {kw_name} 주간 추이 ({start_date}~) ===\n")

    # 분기별 평균
    q_data = {}
    for r in rows:
        week = r[0]
        q = f"{week.year}Q{(week.month - 1) // 3 + 1}"
        if q not in q_data:
            q_data[q] = []
        q_data[q].append(r[1])

    print("분기별 평균 상품 수:")
    for q, vals in sorted(q_data.items()):
        avg = sum(vals) / len(vals)
        bar = "█" * int(avg / 3)
        print(f"  {q}: {avg:6.0f}  {bar}")

    print(f"\n최근 8주:")
    for r in rows[-8:]:
        print(f"  {r[0]} | 상품 {r[1]:>4} | 브랜드 {r[2]:>3}")

    conn.close()


def list_products(kw_name: str, limit: int = 50, period: str = "2026Q1"):
    """특정 기간의 상품 리스트."""
    conn = get_connection()
    cur = conn.cursor()

    config = KEYWORDS[kw_name]
    where = build_where(config)

    # 기간 설정
    if period == "2026Q1":
        date_filter = "UPDATE_DATE >= '2026-01-01' AND UPDATE_DATE < '2026-04-01'"
    elif period == "2026Q2":
        date_filter = "UPDATE_DATE >= '2026-04-01'"
    elif period == "latest":
        date_filter = "UPDATE_DATE >= DATEADD(WEEK, -2, CURRENT_DATE())"
    else:
        date_filter = f"UPDATE_DATE >= '{period}'"

    sql = f"""
        SELECT BRAND, PRODUCT_NAME, MID_CATEGORY, MIN(RANKING) as best_rank,
               MAX(REVIEW_COUNT) as reviews
        FROM DW_MUSINSA_PRDT_RNK_W
        WHERE {date_filter} AND {where}
        GROUP BY BRAND, PRODUCT_NAME, MID_CATEGORY
        ORDER BY best_rank
        LIMIT {limit}
    """
    cur.execute(sql)
    rows = cur.fetchall()

    print(f"\n=== {kw_name} 상품 TOP {limit} ({period}) ===\n")
    print(f"{'#':>3} {'브랜드':<25} {'카테고리':<18} {'상품명'}")
    print("-" * 100)
    for i, r in enumerate(rows, 1):
        brand = r[0] or ""
        name = (r[1] or "")[:55]
        cat = r[2] or ""
        print(f"{i:>3} {brand:<25} {cat:<18} {name}")

    conn.close()


def all_trends():
    """전체 키워드 트렌드 요약."""
    conn = get_connection()
    cur = conn.cursor()

    print("\n=== 전체 키워드 트렌드 요약 (2025~) ===\n")
    print(f"{'키워드':<18} {'25Q1':>6} {'25Q2':>6} {'25Q3':>6} {'25Q4':>6} {'26Q1':>6} {'26Q2':>6}  추세")
    print("-" * 85)

    for kw_name, config in KEYWORDS.items():
        where = build_where(config)
        sql = f"""
            SELECT DATE_TRUNC('QUARTER', UPDATE_DATE)::DATE as quarter,
                   AVG(cnt) as avg_products
            FROM (
                SELECT DATE_TRUNC('WEEK', UPDATE_DATE)::DATE as week,
                       COUNT(DISTINCT PRODUCT_CODE) as cnt
                FROM DW_MUSINSA_PRDT_RNK_W
                WHERE UPDATE_DATE >= '2025-01-01' AND {where}
                GROUP BY week
            )
            GROUP BY quarter
            ORDER BY quarter
        """
        cur.execute(sql)
        rows = cur.fetchall()
        q_vals = {}
        for r in rows:
            q = r[0]
            q_label = f"{q.year % 100}Q{(q.month - 1) // 3 + 1}"
            q_vals[q_label] = r[1]

        vals = [q_vals.get(q, 0) for q in ["25Q1", "25Q2", "25Q3", "25Q4", "26Q1", "26Q2"]]
        trend = ""
        if vals[0] > 0 and vals[-1] > 0:
            change = (vals[-1] - vals[0]) / vals[0] * 100
            trend = f"{'↑' if change > 10 else '↓' if change < -10 else '→'} {change:+.0f}%"

        print(f"{kw_name:<18} {vals[0]:>6.0f} {vals[1]:>6.0f} {vals[2]:>6.0f} {vals[3]:>6.0f} {vals[4]:>6.0f} {vals[5]:>6.0f}  {trend}")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="무신사 키워드 트렌드 분석")
    parser.add_argument("--keyword", "-k", help="특정 키워드 트렌드 (예: 레이스)")
    parser.add_argument("--list-products", "-l", help="상품 리스트 (예: 가죽/레더)")
    parser.add_argument("--limit", type=int, default=50, help="상품 리스트 개수")
    parser.add_argument("--period", default="2026Q1", help="기간 (2026Q1, 2026Q2, latest)")
    parser.add_argument("--all", action="store_true", help="전체 키워드 요약")
    args = parser.parse_args()

    if args.list_products:
        list_products(args.list_products, args.limit, args.period)
    elif args.keyword:
        trend_query(args.keyword)
    elif args.all:
        all_trends()
    else:
        all_trends()


if __name__ == "__main__":
    main()
