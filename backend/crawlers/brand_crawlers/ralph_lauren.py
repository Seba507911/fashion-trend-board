"""Ralph Lauren Korea 크롤러.

대상: https://www.ralphlauren.co.kr
DemandWare 기반, .product-tile 파싱.
Stealth Playwright 필요.
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.ralphlauren.co.kr"

CATEGORY_URLS = {
    "outer": [
        f"{BASE_URL}/ko/men-clothing-outerwear/10014",
        f"{BASE_URL}/ko/women-clothing-outerwear/70014",
    ],
    "inner": [
        f"{BASE_URL}/ko/men-clothing-shirts/10011",
        f"{BASE_URL}/ko/men-clothing-t-shirts-sweatshirts/10010",
        f"{BASE_URL}/ko/men-clothing-sweaters/10009",
        f"{BASE_URL}/ko/men-clothing-polo-shirts/10008",
        f"{BASE_URL}/ko/women-clothing-tops/70009",
        f"{BASE_URL}/ko/women-clothing-sweaters/70011",
    ],
    "bottom": [
        f"{BASE_URL}/ko/men-clothing-pants/10013",
        f"{BASE_URL}/ko/men-clothing-shorts/10012",
        f"{BASE_URL}/ko/women-clothing-pants/70013",
        f"{BASE_URL}/ko/women-clothing-skirts/70015",
    ],
    "wear_etc": [f"{BASE_URL}/ko/women-clothing-dresses/70012"],
    "shoes": [
        f"{BASE_URL}/ko/men-shoes/10015",
        f"{BASE_URL}/ko/women-shoes/70016",
    ],
    "bag": [f"{BASE_URL}/ko/women-accessories-handbags/70019"],
    "acc_etc": [
        f"{BASE_URL}/ko/men-accessories/10016",
        f"{BASE_URL}/ko/women-accessories/70017",
    ],
}


class RalphLaurenCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("ralph_lauren")

    async def get_product_list_urls(self, season=None):
        return [u for urls in CATEGORY_URLS.values() for u in urls]

    def get_card_selector(self):
        return ".product-tile"

    def _url_to_category(self, page_url):
        for cat_id, urls in CATEGORY_URLS.items():
            for u in urls:
                if u == page_url:
                    return cat_id
        return None

    async def crawl(self, season=None, max_pages=18, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth

        products, seen = [], set()
        stealth = Stealth()
        async with async_playwright() as pw:
            stealth.hook_playwright_context(pw)
            browser = await pw.chromium.launch(headless=True)
            page = await (await browser.new_context(
                viewport={"width": 1440, "height": 900}, locale="ko-KR",
            )).new_page()
            try:
                for i, url in enumerate((await self.get_product_list_urls())[:max_pages]):
                    self.logger.info(f"Crawling {i+1}: {url}")
                    cat = self._url_to_category(url)
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        await asyncio.sleep(8)
                        for _ in range(5):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(2)
                        items = await page.evaluate("""() => {
                            return Array.from(document.querySelectorAll('.product-tile')).map(tile => {
                                const link = tile.querySelector('a[href*=".html"]');
                                const nameEl = tile.querySelector('.product-tile__product-name, .product-name, h3');
                                const brandEl = tile.querySelector('.product-tile__brand-name, .brand-name');
                                const priceEl = tile.querySelector('.product-tile__product-price, .price, [class*=price]');
                                const img = tile.querySelector('img');
                                return {
                                    href: link ? link.href : '',
                                    name: nameEl ? nameEl.innerText.trim() : '',
                                    brand: brandEl ? brandEl.innerText.trim() : '',
                                    price: priceEl ? priceEl.innerText.trim() : '',
                                    img: img ? (img.src || '') : '',
                                };
                            }).filter(x => x.name && x.href);
                        }""")
                        for item in items:
                            slug = item["href"].split("/")[-1].split(".")[0].split("?")[0]
                            pid = self.make_product_id(slug[:30])
                            if pid in seen: continue
                            seen.add(pid)
                            price_str = re.sub(r"[^\d]", "", item.get("price", "").split("~")[0].split("\n")[0])
                            raw = {
                                "id": pid, "product_name": item["name"], "product_name_kr": item["name"],
                                "price": int(price_str) if price_str else 0, "sale_price": None, "currency": "KRW",
                                "category_id": cat, "season_id": "2026SS", "colors": [],
                                "thumbnail_url": item["img"], "image_urls": [item["img"]] if item["img"] else [],
                                "product_url": item["href"],
                                "style_tags": ["american", "classic", "preppy"],
                            }
                            products.append(self.normalize_product(raw))
                        self.logger.info(f"Found {len(items)}, total unique: {len(products)}")
                        await asyncio.sleep(3)
                    except Exception as e:
                        self.logger.error(f"Failed: {url} - {e}")
            finally:
                await browser.close()
        self.logger.info(f"Total: {len(products)}")
        return products

    async def parse_product_card(self, page, element):
        return None
