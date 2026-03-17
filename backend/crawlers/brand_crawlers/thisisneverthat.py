"""thisisneverthat 크롤러.

대상: https://www.thisisneverthat.com
SPA (Vite), article 태그 기반 상품 카드.
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.thisisneverthat.com"

CATEGORY_URLS = {
    "outer": [f"{BASE_URL}/collections/outerwear"],
    "inner": [
        f"{BASE_URL}/collections/tops",
        f"{BASE_URL}/collections/sweats",
        f"{BASE_URL}/collections/knit",
    ],
    "bottom": [
        f"{BASE_URL}/collections/bottoms",
    ],
    "acc_etc": [
        f"{BASE_URL}/collections/accessories",
        f"{BASE_URL}/collections/headwear",
    ],
    "bag": [f"{BASE_URL}/collections/bags"],
    "shoes": [f"{BASE_URL}/collections/footwear"],
}


class ThisisneverthatCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("thisisneverthat")

    async def get_product_list_urls(self, season=None):
        return [u for urls in CATEGORY_URLS.values() for u in urls]

    def get_card_selector(self):
        return "article"

    def _url_to_category(self, page_url):
        for cat_id, urls in CATEGORY_URLS.items():
            for u in urls:
                if u == page_url:
                    return cat_id
        return None

    async def crawl(self, season=None, max_pages=12, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright

        products, seen = [], set()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await (await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                viewport={"width": 1440, "height": 900}, locale="ko-KR",
            )).new_page()
            try:
                for i, url in enumerate((await self.get_product_list_urls())[:max_pages]):
                    self.logger.info(f"Crawling {i+1}: {url}")
                    cat = self._url_to_category(url)
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                        await asyncio.sleep(6)
                        for _ in range(8):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(1.5)
                        items = await page.evaluate("""() => {
                            return Array.from(document.querySelectorAll('article')).map(el => {
                                const link = el.querySelector('a[href*="/products/"]');
                                if (!link) return null;
                                const href = link.href;
                                const img = el.querySelector('img');
                                const nameEl = el.querySelector('h3, [class*=name], [class*=title]');
                                const priceEl = el.querySelector('[class*=price], [class*=Price]');
                                const name = nameEl ? nameEl.innerText.trim() :
                                    el.innerText.trim().split('\\n').find(l => l.length > 3 && !l.includes('₩') && !l.includes('KRW')) || '';
                                const price = priceEl ? priceEl.innerText.trim() : '';
                                return {
                                    href, name,
                                    price,
                                    img: img ? (img.src || '') : '',
                                };
                            }).filter(x => x && x.name && x.href);
                        }""")
                        for item in items:
                            slug = item["href"].split("/products/")[-1].split("?")[0] if "/products/" in item["href"] else ""
                            if not slug:
                                continue
                            pid = self.make_product_id(slug[:40])
                            if pid in seen:
                                continue
                            seen.add(pid)
                            price_str = re.sub(r"[^\d]", "", item.get("price", "").split("~")[0].split("\n")[0])
                            raw = {
                                "id": pid, "product_name": item["name"], "product_name_kr": item["name"],
                                "price": int(price_str) if price_str else 0, "sale_price": None, "currency": "KRW",
                                "category_id": cat, "season_id": "2026SS", "colors": [],
                                "thumbnail_url": item["img"], "image_urls": [item["img"]] if item["img"] else [],
                                "product_url": item["href"],
                                "style_tags": ["street", "contemporary"],
                            }
                            products.append(self.normalize_product(raw))
                        self.logger.info(f"Found {len(items)}, total unique: {len(products)}")
                        await asyncio.sleep(2)
                    except Exception as e:
                        self.logger.error(f"Failed: {url} - {e}")
            finally:
                await browser.close()
        self.logger.info(f"Total: {len(products)}")
        return products

    async def parse_product_card(self, page, element):
        return None
