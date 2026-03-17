"""On Running Korea 크롤러.

대상: https://www.on.com/ko-kr/
Nuxt.js SPA, article 태그 기반.
카테고리: /ko-kr/shop/{gender}/{category}
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.on.com"

CATEGORY_URLS = {
    "shoes": [
        f"{BASE_URL}/ko-kr/shop/mens/shoes",
        f"{BASE_URL}/ko-kr/shop/womens/shoes",
    ],
    "top": [
        f"{BASE_URL}/ko-kr/shop/mens/tops",
        f"{BASE_URL}/ko-kr/shop/womens/tops",
    ],
    "outer": [
        f"{BASE_URL}/ko-kr/shop/mens/outerwear",
        f"{BASE_URL}/ko-kr/shop/womens/outerwear",
    ],
    "bottom": [
        f"{BASE_URL}/ko-kr/shop/mens/pants-and-tights",
        f"{BASE_URL}/ko-kr/shop/womens/pants-and-tights",
    ],
    "accessories": [
        f"{BASE_URL}/ko-kr/shop/mens/accessories",
        f"{BASE_URL}/ko-kr/shop/womens/accessories",
    ],
}


class OnRunningCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("on_running")

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
                        for _ in range(8):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(1.5)
                        items = await page.evaluate("""() => {
                            const badges = ['베스트 셀러','곧 출시 예정','신제품','새로운 색상','리미티드 에디션','남성','여성','유니섹스','NEW','BEST','LIMITED'];
                            return Array.from(document.querySelectorAll('article')).map(el => {
                                const link = el.querySelector('a[href*="/products/"]');
                                if (!link) return null;
                                const text = el.innerText.trim();
                                const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                                let name = '', price = '', desc = '';
                                for (const line of lines) {
                                    if (line.startsWith('₩') || line.includes('₩')) { price = line; continue; }
                                    const isBadge = badges.some(b => line === b || line.startsWith(b));
                                    if (isBadge) continue;
                                    // Description lines contain gender/use-case keywords
                                    if (line.includes('데일리') || line.includes('러닝') || line.includes('트레일') || line.includes('주행') || line.includes('퍼포먼스') || line.includes('쿠셔닝')) { desc = line; continue; }
                                    if (!name && line.length > 2) name = line;
                                }
                                const img = el.querySelector('img');
                                let imgSrc = img ? (img.src || '') : '';
                                // Add size param to Contentful images for faster loading
                                if (imgSrc.includes('ctfassets.net') && !imgSrc.includes('?w=')) {
                                    imgSrc += '?w=480&fm=webp';
                                }
                                return {
                                    href: link.href,
                                    name: name,
                                    price: price,
                                    img: imgSrc,
                                };
                            }).filter(x => x && x.name && x.href);
                        }""")
                        for item in items:
                            slug = item["href"].split("/products/")[-1].split("/")[0] if "/products/" in item["href"] else ""
                            if not slug:
                                continue
                            pid = self.make_product_id(slug[:40])
                            if pid in seen:
                                continue
                            seen.add(pid)
                            price_str = re.sub(r"[^\d]", "", item.get("price", ""))
                            raw = {
                                "id": pid, "product_name": item["name"], "product_name_kr": item["name"],
                                "price": int(price_str) if price_str else 0, "sale_price": None, "currency": "KRW",
                                "category_id": cat, "season_id": "2026SS", "colors": [],
                                "thumbnail_url": item["img"], "image_urls": [item["img"]] if item["img"] else [],
                                "product_url": item["href"],
                                "style_tags": ["running", "athleisure", "performance"],
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
