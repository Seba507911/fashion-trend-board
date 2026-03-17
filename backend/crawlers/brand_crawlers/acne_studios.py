"""Acne Studios Korea 크롤러.

대상: https://www.acnestudios.com/kr/
카테고리: /kr/en/{gender}/{category}/
상품 카드: .product-tile (data-gtm에 상품 정보 JSON 포함)
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import Optional

from playwright.async_api import Page

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.acnestudios.com"

CATEGORY_URLS = {
    "outer": [
        f"{BASE_URL}/kr/en/man/clothing/outerwear/",
        f"{BASE_URL}/kr/en/woman/clothing/outerwear/",
    ],
    "top": [
        f"{BASE_URL}/kr/en/man/clothing/t-shirts/",
        f"{BASE_URL}/kr/en/man/clothing/sweatshirts/",
        f"{BASE_URL}/kr/en/man/clothing/knitwear/",
        f"{BASE_URL}/kr/en/man/clothing/shirts/",
        f"{BASE_URL}/kr/en/woman/clothing/t-shirts/",
        f"{BASE_URL}/kr/en/woman/clothing/knitwear/",
        f"{BASE_URL}/kr/en/woman/clothing/tops/",
    ],
    "bottom": [
        f"{BASE_URL}/kr/en/man/clothing/trousers/",
        f"{BASE_URL}/kr/en/man/clothing/denim/",
        f"{BASE_URL}/kr/en/woman/clothing/trousers/",
        f"{BASE_URL}/kr/en/woman/clothing/denim/",
    ],
    "shoes": [
        f"{BASE_URL}/kr/en/man/shoes/",
        f"{BASE_URL}/kr/en/woman/shoes/",
    ],
    "bag": [
        f"{BASE_URL}/kr/en/man/bags/",
        f"{BASE_URL}/kr/en/woman/bags/",
    ],
    "accessories": [
        f"{BASE_URL}/kr/en/man/accessories/",
        f"{BASE_URL}/kr/en/woman/accessories/",
    ],
}


class AcneStudiosCrawler(BaseCrawler):
    """아크네 스튜디오 크롤러."""

    def __init__(self):
        super().__init__("acne_studios")

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

    async def crawl(self, season=None, max_pages=20, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright

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

                        # Scroll to load all
                        for _ in range(5):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(2)

                        items = await page.evaluate("""() => {
                            const results = [];
                            const tiles = document.querySelectorAll('.product-tile');
                            tiles.forEach(tile => {
                                // data-gtm has product info as JSON
                                const gtmStr = tile.getAttribute('data-gtm') || '{}';
                                let gtm = {};
                                try { gtm = JSON.parse(gtmStr); } catch(e) {}

                                const link = tile.querySelector('a[href*="/kr/"]');
                                const href = link ? link.getAttribute('href') : '';

                                const img = tile.querySelector('img');
                                const imgSrc = img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : '';

                                const nameEl = tile.querySelector('.tile__product-name, .product-name');
                                const name = nameEl ? nameEl.innerText.trim() : (gtm.name || '');

                                const priceEl = tile.querySelector('.tile__product-price, .product-price');
                                const priceText = priceEl ? priceEl.innerText.trim() : '';

                                const id = gtm.id || tile.id || '';

                                if (name || id) {
                                    results.push({
                                        id: id,
                                        name: name,
                                        href: href,
                                        priceText: priceText,
                                        price: parseInt(gtm.price) || 0,
                                        imgSrc: imgSrc,
                                        category: gtm.category || '',
                                    });
                                }
                            });
                            return results;
                        }""")

                        for item in items:
                            prod_id = item.get("id", "")
                            if not prod_id:
                                continue
                            pid = self.make_product_id(prod_id)
                            if pid in seen_ids:
                                continue
                            seen_ids.add(pid)

                            price = item.get("price", 0)
                            if not price:
                                price = int(re.sub(r"[^\d]", "", item.get("priceText", "").split("~")[0]) or 0)

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
                                "colors": [],
                                "thumbnail_url": img_url,
                                "image_urls": [img_url] if img_url else [],
                                "product_url": product_url,
                                "style_tags": ["minimal", "scandinavian", "contemporary"],
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
