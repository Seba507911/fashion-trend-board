"""Maison Kitsuné Korea 크롤러.

대상: https://www.maisonkitsune.com/kr/
카테고리: /kr/{gender}/categories/{category}.html
상품 카드: .product-item (Magento 기반)
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.maisonkitsune.com"

# Main category pages (sub-category pages don't render product-items)
CATEGORY_URLS = {
    "all_men": [f"{BASE_URL}/kr/man/categories.html"],
    "all_women": [f"{BASE_URL}/kr/woman/categories.html"],
}


class MaisonKitsuneCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("maison_kitsune")

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

    async def crawl(self, season=None, max_pages=20, dry_run=False, fetch_details=False):
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
                        for _ in range(3):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(1.5)
                        items = await page.evaluate("""() => {
                            return Array.from(document.querySelectorAll('.product-item')).map(el => {
                                const link = el.querySelector('a[href]');
                                const nameEl = el.querySelector('.product-item-info .product-name, .product-item-link');
                                const priceEl = el.querySelector('.price, .price-wrapper [data-price-amount]');
                                const img = el.querySelector('img');
                                return {
                                    href: link ? link.href : '',
                                    name: nameEl ? nameEl.innerText.trim() : (link ? link.innerText.trim().split('\\n')[0] : ''),
                                    price: priceEl ? priceEl.getAttribute('data-price-amount') || priceEl.innerText.trim() : '',
                                    img: img ? (img.src || img.dataset.src || '') : '',
                                };
                            }).filter(x => x.name && x.href);
                        }""")
                        for item in items:
                            slug = item["href"].split("/")[-1].split("?")[0].split(".")[0]
                            pid = self.make_product_id(slug[:30])
                            if pid in seen: continue
                            seen.add(pid)
                            price_str = re.sub(r"[^\d]", "", item.get("price", "").split(".")[0])
                            raw = {
                                "id": pid, "product_name": item["name"], "product_name_kr": item["name"],
                                "price": int(price_str) if price_str else 0, "sale_price": None, "currency": "KRW",
                                "category_id": cat, "season_id": "2026SS", "colors": [],
                                "thumbnail_url": item["img"], "image_urls": [item["img"]] if item["img"] else [],
                                "product_url": item["href"], "style_tags": ["french", "contemporary"],
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
