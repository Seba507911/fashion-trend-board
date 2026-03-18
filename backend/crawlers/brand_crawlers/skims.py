"""SKIMS 크롤러.

대상: https://skims.com
Shopify 기반이지만 커스텀 React 테마 → Playwright로 .product-card 파싱.
"""
from __future__ import annotations

import asyncio
import re

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://skims.com"

CATEGORY_URLS = {
    "inner": [
        f"{BASE_URL}/collections/tops",
        f"{BASE_URL}/collections/bodysuits",
        f"{BASE_URL}/collections/loungewear",
    ],
    "bottom": [f"{BASE_URL}/collections/bottoms"],
    "outer": [f"{BASE_URL}/collections/outerwear"],
    "wear_etc": [f"{BASE_URL}/collections/dresses"],
    "acc_etc": [f"{BASE_URL}/collections/accessories"],
}


class SkimsCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("skims")

    async def get_product_list_urls(self, season=None):
        return [u for urls in CATEGORY_URLS.values() for u in urls]

    def get_card_selector(self):
        return ".product-card"

    def _url_to_category(self, page_url):
        for cat_id, urls in CATEGORY_URLS.items():
            for u in urls:
                if u == page_url:
                    return cat_id
        return None

    async def crawl(self, season=None, max_pages=8, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright

        products, seen = [], set()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await (await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                viewport={"width": 1440, "height": 900}, locale="en-US",
            )).new_page()
            try:
                for i, url in enumerate((await self.get_product_list_urls())[:max_pages]):
                    self.logger.info(f"Crawling {i+1}: {url}")
                    cat = self._url_to_category(url)
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                        await asyncio.sleep(8)
                        for _ in range(8):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(1.5)
                        items = await page.evaluate("""() => {
                            return Array.from(document.querySelectorAll('.product-card')).map(card => {
                                const link = card.querySelector('a[href*="/products/"]');
                                if (!link) return null;
                                const href = link.href;
                                const slug = href.split('/products/')[1]?.split('?')[0];
                                const img = card.querySelector('img');
                                const imgSrc = img ? (img.src || '') : '';
                                // Name and price from text
                                const text = card.innerText.trim();
                                const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 1);
                                let name = '', price = '';
                                for (const l of lines) {
                                    if (l.startsWith('$') || l.includes('$')) { price = l; continue; }
                                    if (l === 'NEW' || l === 'BEST SELLER' || l === 'WAITLIST') continue;
                                    if (!name && l.length > 2) name = l;
                                }
                                return { slug, href, name, price, img: imgSrc };
                            }).filter(x => x && x.slug && x.name);
                        }""")
                        for item in items:
                            pid = self.make_product_id(item["slug"][:40])
                            if pid in seen: continue
                            seen.add(pid)
                            price_str = re.sub(r"[^\d.]", "", item.get("price", "").split("-")[0])
                            raw = {
                                "id": pid, "product_name": item["name"], "product_name_kr": item["name"],
                                "price": int(float(price_str)) if price_str else 0, "sale_price": None, "currency": "USD",
                                "category_id": cat, "season_id": "2026SS", "colors": [],
                                "thumbnail_url": item["img"], "image_urls": [item["img"]] if item["img"] else [],
                                "product_url": item["href"],
                                "style_tags": ["bodycon", "athleisure", "contemporary"],
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
