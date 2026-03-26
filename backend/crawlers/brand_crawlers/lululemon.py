"""Lululemon Korea 공식몰 크롤러.

대상: https://www.lululemon.co.kr
카테고리: /ko-kr/c/{category}/
상품 카드: .product-tile (DemandWare 기반)
Playwright 기반 (SSR + JS 렌더링)
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from playwright.async_api import Page

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.lululemon.co.kr"

CATEGORY_URLS = {
    "inner": [
        f"{BASE_URL}/ko-kr/c/womens-tops/",
        f"{BASE_URL}/ko-kr/c/mens-tops/",
        f"{BASE_URL}/ko-kr/c/womens-long-sleeve-shirts/",
        f"{BASE_URL}/ko-kr/c/mens-hoodies-sweatshirts/",
    ],
    "outer": [
        f"{BASE_URL}/ko-kr/c/jackets-outerwear/",
        f"{BASE_URL}/ko-kr/c/mens-coats-and-jackets/",
    ],
    "bottom": [
        f"{BASE_URL}/ko-kr/c/womens-leggings/",
        f"{BASE_URL}/ko-kr/c/womens-pants/",
        f"{BASE_URL}/ko-kr/c/womens-shorts/",
        f"{BASE_URL}/ko-kr/c/mens-pants/",
        f"{BASE_URL}/ko-kr/c/mens-shorts/",
    ],
    "wear_etc": [
        f"{BASE_URL}/ko-kr/c/skirts-dresses-rompers/",
    ],
    "bag": [
        f"{BASE_URL}/ko-kr/c/bags/",
    ],
    "acc_etc": [
        f"{BASE_URL}/ko-kr/c/accessories/",
    ],
}


class LululemonCrawler(BaseCrawler):
    """룰루레몬 코리아 크롤러."""

    def __init__(self):
        super().__init__("lululemon")

    async def get_product_list_urls(self, season=None):
        urls = []
        for cat_urls in CATEGORY_URLS.values():
            urls.extend(cat_urls)
        return urls

    def get_card_selector(self):
        return ".product-tile"

    def _url_to_category(self, page_url):
        for cat_id, cat_urls in CATEGORY_URLS.items():
            for curl in cat_urls:
                if curl.rstrip("/") in page_url:
                    return cat_id
        return None

    async def crawl(self, season=None, max_pages=10, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright
        import json

        products = []
        seen_ids = set()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1440, "height": 900},
            )
            page = await context.new_page()

            try:
                urls = await self.get_product_list_urls(season)
                for i, url in enumerate(urls[:max_pages]):
                    self.logger.info(f"Crawling page {i + 1}/{len(urls)}: {url}")
                    category_id = self._url_to_category(url)

                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        await asyncio.sleep(5)

                        # Scroll to load more
                        for _ in range(10):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(2)

                        items = await page.evaluate("""() => {
                            const results = [];
                            const tiles = document.querySelectorAll('.product-tile');
                            tiles.forEach(tile => {
                                const id = tile.id || '';
                                const link = tile.querySelector('a[href*="/ko-kr/p/"]');
                                const href = link ? link.getAttribute('href') : '';

                                // Name from aria-label or text
                                const nameEl = tile.querySelector('.product-tile__product-name, .product-name, a[aria-label]');
                                let name = '';
                                if (nameEl) {
                                    name = nameEl.getAttribute('aria-label') || nameEl.innerText || '';
                                    name = name.replace(/^더보기\\s*/, '').trim();
                                }

                                // Price
                                const priceEl = tile.querySelector('.product-tile__product-price, .price-sales, .product-price');
                                const priceText = priceEl ? priceEl.innerText.trim() : '';

                                // Image
                                const img = tile.querySelector('img');
                                const imgSrc = img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : '';

                                // Color
                                const colorSwatches = tile.querySelectorAll('.swatch-circle, .color-swatch');
                                const colors = [];
                                colorSwatches.forEach(s => {
                                    const title = s.getAttribute('title') || s.getAttribute('aria-label') || '';
                                    if (title) colors.push(title);
                                });

                                if (name && href) {
                                    results.push({id, name, href, priceText, imgSrc, colors});
                                }
                            });
                            return results;
                        }""")

                        for item in items:
                            prod_id = item.get("id", "").replace("prod", "")
                            if not prod_id:
                                prod_id = re.sub(r"[^a-zA-Z0-9]", "", item.get("name", ""))[:20]
                            pid = self.make_product_id(prod_id)
                            if pid in seen_ids:
                                continue
                            seen_ids.add(pid)

                            price_text = item.get("priceText", "")
                            price = int(re.sub(r"[^\d]", "", price_text.split("~")[0].split("-")[0]) or 0)

                            img_url = item.get("imgSrc", "")
                            href = item.get("href", "")
                            product_url = href if href.startswith("http") else f"{BASE_URL}{href}"

                            raw = {
                                "id": pid,
                                "product_name": item["name"],
                                "product_name_kr": item["name"],
                                "price": price,
                                "sale_price": None,
                                "currency": "KRW",
                                "category_id": category_id,
                                "season_id": "2026SS",
                                "colors": item.get("colors", []),
                                "thumbnail_url": img_url,
                                "image_urls": [img_url] if img_url else [],
                                "product_url": product_url,
                                "style_tags": ["athleisure", "yoga", "activewear"],
                            }
                            product = self.normalize_product(raw)
                            products.append(product)

                            if dry_run:
                                self.logger.info(f"  [DRY] {product['product_name']} - {price} KRW")

                        self.logger.info(f"Found {len(items)} items, total unique: {len(products)}")
                        await asyncio.sleep(2)

                    except Exception as e:
                        self.logger.error(f"Page crawl failed: {url} - {e}")
                        continue
            finally:
                await browser.close()

        self.logger.info(f"Total crawled: {len(products)} products")
        return products

    async def parse_product_card(self, page, element):
        return None
