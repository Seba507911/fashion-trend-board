"""크롤링 실행 스크립트.

플랫폼 기반 크롤러를 사용하여 브랜드 상품을 크롤링한다.
브랜드 추가는 backend/crawlers/brand_configs.py에서 설정.

Usage:
    python scripts/run_crawl.py --brand marithe --details
    python scripts/run_crawl.py --brand alo --dry-run
    python scripts/run_crawl.py --list
"""
import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.crawlers.brand_configs import get_crawler, list_brands
from backend.db.database import DB_PATH

logging.basicConfig(level=logging.INFO, format="%(name)s | %(levelname)s | %(message)s")


async def save_products(products: list[dict]):
    """크롤링 결과를 DB에 저장."""
    import aiosqlite

    async with aiosqlite.connect(str(DB_PATH)) as db:
        for p in products:
            await db.execute(
                """INSERT OR REPLACE INTO products
                   (id, brand_id, season_id, category_id, product_name, product_name_kr,
                    price, sale_price, currency, colors, materials, image_urls,
                    thumbnail_url, product_url, style_tags, sizes, fit_info,
                    description, is_active, crawled_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    p["id"], p["brand_id"], p.get("season_id"), p.get("category_id"),
                    p["product_name"], p.get("product_name_kr"),
                    p.get("price"), p.get("sale_price"), p.get("currency", "KRW"),
                    p.get("colors", "[]"), p.get("materials", "[]"), p.get("image_urls", "[]"),
                    p.get("thumbnail_url"), p.get("product_url"),
                    p.get("style_tags", "[]"), p.get("sizes", "[]"), p.get("fit_info"),
                    p.get("description"),
                    p.get("is_active", 1), p.get("crawled_at"),
                ),
            )
        await db.commit()
        logging.info(f"Saved {len(products)} products to DB")


async def main():
    parser = argparse.ArgumentParser(description="FTIB Crawler")
    parser.add_argument("--brand", help="Brand ID to crawl")
    parser.add_argument("--season", default=None)
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="상품 수 제한 (테스트용)")
    parser.add_argument("--details", action="store_true", help="상세 페이지 크롤링 포함")
    parser.add_argument("--list", action="store_true", help="등록된 브랜드 목록 표시")
    args = parser.parse_args()

    if args.list:
        brands = list_brands()
        print(f"\n{'Brand':20s} {'Platform':10s}")
        print("-" * 32)
        for brand_id, platform in sorted(brands.items()):
            print(f"{brand_id:20s} {platform:10s}")
        print(f"\nTotal: {len(brands)} brands")
        return

    if not args.brand:
        parser.error("--brand is required (or use --list)")

    brands = list(list_brands().keys()) if args.brand == "all" else [args.brand]

    for brand_id in brands:
        try:
            crawler = get_crawler(brand_id)
        except ValueError as e:
            logging.error(str(e))
            continue

        logging.info(f"=== Starting crawl: {brand_id} ===")
        products = await crawler.crawl(
            season=args.season,
            max_pages=args.max_pages,
            dry_run=args.dry_run,
            fetch_details=args.details,
        )

        if args.limit:
            products = products[: args.limit]

        if args.dry_run:
            print(json.dumps(products[:3], indent=2, ensure_ascii=False))
            print(f"... total {len(products)} products (dry run)")
        else:
            await save_products(products)


if __name__ == "__main__":
    asyncio.run(main())
