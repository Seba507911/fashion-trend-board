"""Supreme 크롤러.

대상: https://www.supremenewyork.com/shop
자체 플랫폼, a[href*="/products/"] 기반.
"""
from __future__ import annotations

import asyncio
import re

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.supremenewyork.com"

CATEGORY_URLS = {
    "outer": [f"{BASE_URL}/shop/jackets"],
    "inner": [
        f"{BASE_URL}/shop/shirts",
        f"{BASE_URL}/shop/tops-sweaters",
        f"{BASE_URL}/shop/t-shirts",
        f"{BASE_URL}/shop/sweatshirts",
    ],
    "bottom": [f"{BASE_URL}/shop/pants"],
    "headwear": [f"{BASE_URL}/shop/hats"],
    "bag": [f"{BASE_URL}/shop/bags"],
    "shoes": [f"{BASE_URL}/shop/shoes"],
    "acc_etc": [f"{BASE_URL}/shop/accessories"],
}


class SupremeCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("supreme")

    async def get_product_list_urls(self, season=None):
        return [u for urls in CATEGORY_URLS.values() for u in urls]

    def get_card_selector(self):
        return "a[href*='/products/']"

    def _url_to_category(self, page_url):
        for cat_id, urls in CATEGORY_URLS.items():
            for u in urls:
                if u == page_url:
                    return cat_id
        return None

    async def crawl(self, season=None, max_pages=10, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth

        products, seen = [], set()
        stealth = Stealth()
        async with async_playwright() as pw:
            stealth.hook_playwright_context(pw)
            browser = await pw.chromium.launch(headless=True)
            page = await (await browser.new_context(
                viewport={"width": 1440, "height": 900}, locale="en-US",
            )).new_page()
            try:
                for i, url in enumerate((await self.get_product_list_urls())[:max_pages]):
                    self.logger.info(f"Crawling {i+1}: {url}")
                    cat = self._url_to_category(url)
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                        await asyncio.sleep(6)
                        for _ in range(5):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(1.5)
                        items = await page.evaluate("""() => {
                            const links = document.querySelectorAll('a[href*="/products/"]');
                            const seen = new Set();
                            return Array.from(links).map(a => {
                                const href = a.href;
                                const slug = href.split('/products/')[1]?.split('?')[0]?.split('/')[0];
                                if (!slug || seen.has(slug)) return null;
                                seen.add(slug);
                                const img = a.querySelector('img');
                                const text = a.innerText.trim();
                                const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 1);
                                let name = '', price = '';
                                for (const l of lines) {
                                    if (l.startsWith('$') || l.startsWith('¥') || l.startsWith('£')) { price = l; continue; }
                                    if (!name) name = l;
                                }
                                return {
                                    slug, href, name, price,
                                    img: img ? (img.src || '') : '',
                                };
                            }).filter(x => x && x.name);
                        }""")
                        for item in items:
                            pid = self.make_product_id(item["slug"][:40])
                            if pid in seen: continue
                            seen.add(pid)
                            price_str = re.sub(r"[^\d]", "", item.get("price", ""))
                            raw = {
                                "id": pid, "product_name": item["name"], "product_name_kr": item["name"],
                                "price": int(price_str) if price_str else 0, "sale_price": None, "currency": "USD",
                                "category_id": cat, "season_id": "2026SS", "colors": [],
                                "thumbnail_url": item["img"], "image_urls": [item["img"]] if item["img"] else [],
                                "product_url": item["href"],
                                "style_tags": ["street", "hype", "skate"],
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
