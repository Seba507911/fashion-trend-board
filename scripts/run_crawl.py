"""크롤링 실행 스크립트."""
import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.crawlers.brand_crawlers.asics import AsicsCrawler
from backend.crawlers.brand_crawlers.newbalance import NewBalanceCrawler
from backend.crawlers.brand_crawlers.marithe import MaritheCrawler
from backend.crawlers.brand_crawlers.alo import AloCrawler
from backend.db.database import DB_PATH

logging.basicConfig(level=logging.INFO, format="%(name)s | %(levelname)s | %(message)s")

CRAWLERS = {
    "asics": AsicsCrawler,
    "newbalance": NewBalanceCrawler,
    "marithe": MaritheCrawler,
    "alo": AloCrawler,
}


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
    parser.add_argument("--brand", required=True, choices=list(CRAWLERS.keys()) + ["all"])
    parser.add_argument("--season", default=None)
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="상품 수 제한 (테스트용)")
    parser.add_argument("--details", action="store_true", help="상세 페이지 크롤링 포함")
    args = parser.parse_args()

    brands = list(CRAWLERS.keys()) if args.brand == "all" else [args.brand]

    for brand_id in brands:
        crawler = CRAWLERS[brand_id]()
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
