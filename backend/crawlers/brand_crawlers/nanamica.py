"""nanamica 공식 온라인 스토어 크롤러.

대상: https://www.nanamica.com/
상품 목록: /itemlist/?cid1={brand}&cid2={category}
상품 카드: a[href*="/item/"] 내 이름, 가격, 이미지
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.nanamica.com"

# cid1=1: nanamica, cid1=2: SELECTION, cid1=3: THE NORTH FACE Purple Label
CATEGORY_URLS = {
    "outer": [f"{BASE_URL}/itemlist/?cid1=1&cid2=3"],     # nanamica OUTER
    "inner": [f"{BASE_URL}/itemlist/?cid1=1&cid2=4"],       # nanamica TOPS
    "bottom": [f"{BASE_URL}/itemlist/?cid1=1&cid2=5"],    # nanamica BOTTOMS
    "bag": [f"{BASE_URL}/itemlist/?cid1=1&cid2=7"],       # nanamica BAGS
    "acc_etc": [f"{BASE_URL}/itemlist/?cid1=1&cid2=8"],# nanamica ACCESSORIES
}


class NanamicaCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("nanamica")

    async def get_product_list_urls(self, season=None):
        return [u for urls in CATEGORY_URLS.values() for u in urls]

    def get_card_selector(self):
        return "a[href*='/item/']"

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
                viewport={"width": 1440, "height": 900}, locale="ja-JP",
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
                            await asyncio.sleep(1)
                        items = await page.evaluate("""() => {
                            const links = document.querySelectorAll('a[href*="/item/"]');
                            const seen = new Set();
                            return Array.from(links).map(a => {
                                const href = a.href;
                                const match = href.match(/\\/item\\/(\\d+)/);
                                if (!match || seen.has(match[1])) return null;
                                seen.add(match[1]);
                                const text = a.innerText.trim();
                                const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                                let name = '', price = '', brand = '';
                                for (const line of lines) {
                                    if (line.includes('YEN') || line.includes('¥')) { price = line; continue; }
                                    if (line === 'nanamica' || line === 'THE NORTH FACE Purple Label') { brand = line; continue; }
                                    if (!name && line.length > 2) name = line;
                                }
                                const img = a.querySelector('img');
                                return {
                                    id: match[1], href, name, price, brand,
                                    img: img ? (img.src || '') : '',
                                };
                            }).filter(x => x && x.name);
                        }""")
                        for item in items:
                            pid = self.make_product_id(item["id"])
                            if pid in seen:
                                continue
                            seen.add(pid)
                            price_str = re.sub(r"[^\d]", "", item.get("price", "").split(".")[0])
                            raw = {
                                "id": pid, "product_name": item["name"], "product_name_kr": item["name"],
                                "price": int(price_str) if price_str else 0, "sale_price": None, "currency": "JPY",
                                "category_id": cat, "season_id": "2026SS", "colors": [],
                                "thumbnail_url": item["img"], "image_urls": [item["img"]] if item["img"] else [],
                                "product_url": item["href"],
                                "style_tags": ["japanese", "contemporary", "outdoor"],
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
