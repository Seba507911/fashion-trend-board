"""BODE 크롤러.

대상: https://www.bodenewyork.com
Shopify 기반, .product-tile 커스텀 테마 → Playwright 파싱.
"""
from __future__ import annotations

import asyncio
import re

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.bodenewyork.com"

CATEGORY_URLS = {
    "outer": [f"{BASE_URL}/collections/mens-outerwear"],
    "inner": [
        f"{BASE_URL}/collections/mens-shirts",
        f"{BASE_URL}/collections/mens-cut-sew",
        f"{BASE_URL}/collections/mens-knitwear",
    ],
    "bottom": [
        f"{BASE_URL}/collections/mens-trousers",
        f"{BASE_URL}/collections/mens-shorts",
    ],
    "shoes": [f"{BASE_URL}/collections/mens-shoes"],
    "acc_etc": [f"{BASE_URL}/collections/accessories"],
}


class BodeCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("bode")

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

    async def crawl(self, season=None, max_pages=10, dry_run=False, fetch_details=False):
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
                        for _ in range(5):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(1.5)
                        items = await page.evaluate("""() => {
                            return Array.from(document.querySelectorAll('.product-tile')).map(tile => {
                                const link = tile.querySelector('a[href*="/products/"]');
                                if (!link) return null;
                                const href = link.href;
                                const slug = href.split('/products/')[1]?.split('?')[0];
                                // Image: try img.src first, then picture source
                                const img = tile.querySelector('img');
                                let imgSrc = img ? (img.src || '') : '';
                                if (!imgSrc || imgSrc.includes('data:image')) {
                                    const source = tile.querySelector('picture source[srcset]');
                                    if (source) {
                                        const srcset = source.srcset;
                                        imgSrc = srcset.split(',').pop().trim().split(' ')[0];
                                    }
                                }
                                if (imgSrc.startsWith('//')) imgSrc = 'https:' + imgSrc;
                                // Name and price
                                const nameEl = tile.querySelector('.product-tile__name, .product-tile__title, h3');
                                const priceEl = tile.querySelector('.product-tile__price, .price');
                                const name = nameEl ? nameEl.innerText.trim() : '';
                                const price = priceEl ? priceEl.innerText.trim() : '';
                                // Fallback name from link text
                                const finalName = name || link.innerText.trim().split('\\n')[0];
                                return { slug, href, name: finalName, price, img: imgSrc };
                            }).filter(x => x && x.slug);
                        }""")
                        for item in items:
                            pid = self.make_product_id(item["slug"][:40])
                            if pid in seen: continue
                            seen.add(pid)
                            price_str = re.sub(r"[^\d.]", "", item.get("price", "").split("-")[0])
                            raw = {
                                "id": pid, "product_name": item["name"] or item["slug"], "product_name_kr": item["name"] or item["slug"],
                                "price": int(float(price_str)) if price_str else 0, "sale_price": None, "currency": "USD",
                                "category_id": cat, "season_id": "2026SS", "colors": [],
                                "thumbnail_url": item["img"], "image_urls": [item["img"]] if item["img"] else [],
                                "product_url": item["href"],
                                "style_tags": ["american", "artisanal", "luxury"],
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
