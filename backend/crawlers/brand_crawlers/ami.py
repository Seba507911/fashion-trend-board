"""Ami Paris Korea 크롤러.

대상: https://www.amiparis.com/ko-kr/
Shopify 기반이지만 커스텀 테마 → Playwright로 .product-item 파싱.
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.amiparis.com"

CATEGORY_URLS = {
    "outer": [f"{BASE_URL}/ko-kr/shopping/man-coats-jackets"],
    "top": [
        f"{BASE_URL}/ko-kr/shopping/man-t-shirts-polos",
        f"{BASE_URL}/ko-kr/shopping/man-knitwear",
        f"{BASE_URL}/ko-kr/shopping/man-shirts",
        f"{BASE_URL}/ko-kr/shopping/man-sweatshirts",
        f"{BASE_URL}/ko-kr/shopping/woman-tops",
    ],
    "bottom": [
        f"{BASE_URL}/ko-kr/shopping/man-trousers",
        f"{BASE_URL}/ko-kr/shopping/woman-trousers",
    ],
    "shoes": [f"{BASE_URL}/ko-kr/shopping/man-shoes"],
    "bag": [f"{BASE_URL}/ko-kr/shopping/man-bags", f"{BASE_URL}/ko-kr/shopping/woman-bags"],
    "accessories": [f"{BASE_URL}/ko-kr/shopping/man-accessories"],
}


class AmiCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("ami")

    async def get_product_list_urls(self, season=None):
        return [u for urls in CATEGORY_URLS.values() for u in urls]

    def get_card_selector(self):
        return ".product-item"

    def _url_to_category(self, page_url):
        for cat_id, urls in CATEGORY_URLS.items():
            for u in urls:
                if u == page_url:
                    return cat_id
        return None

    async def crawl(self, season=None, max_pages=15, dry_run=False, fetch_details=False):
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
                        await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                        await asyncio.sleep(8)
                        for _ in range(5):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(1.5)
                        items = await page.evaluate("""() => {
                            return Array.from(document.querySelectorAll('.product-item')).map(el => {
                                const link = el.querySelector('a[href*="/products/"]');
                                const nameEl = el.querySelector('.product-item__title, .product-name, h3');
                                const priceEl = el.querySelector('.product-item__price, .price, [class*=price]');
                                const img = el.querySelector('img');
                                return {
                                    href: link ? link.href : '',
                                    name: nameEl ? nameEl.innerText.trim() : el.innerText.trim().split('\\n')[0],
                                    price: priceEl ? priceEl.innerText.trim() : '',
                                    img: img ? (img.src || '') : '',
                                };
                            }).filter(x => x.name && x.href);
                        }""")
                        for item in items:
                            slug = item["href"].split("/products/")[-1].split("?")[0] if "/products/" in item["href"] else ""
                            if not slug: continue
                            pid = self.make_product_id(slug[:30])
                            if pid in seen: continue
                            seen.add(pid)
                            price_str = re.sub(r"[^\d]", "", item.get("price", "").split("KRW")[0].replace(",", ""))
                            raw = {
                                "id": pid, "product_name": item["name"], "product_name_kr": item["name"],
                                "price": int(price_str) if price_str else 0, "sale_price": None, "currency": "KRW",
                                "category_id": cat, "season_id": "2026SS", "colors": [],
                                "thumbnail_url": item["img"], "image_urls": [item["img"]] if item["img"] else [],
                                "product_url": item["href"], "style_tags": ["french", "contemporary", "luxury"],
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
