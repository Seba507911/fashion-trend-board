"""Patagonia Korea 크롤러. [class*=card] 기반."""
from __future__ import annotations
import asyncio, re
from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.patagonia.co.kr"
CATEGORIES = {
    "outer": [f"{BASE_URL}/shop/womens-jackets-vests", f"{BASE_URL}/shop/mens-jackets-vests"],
    "inner": [f"{BASE_URL}/shop/womens-tops", f"{BASE_URL}/shop/mens-tops"],
    "bottom": [f"{BASE_URL}/shop/womens-pants-jeans-shorts", f"{BASE_URL}/shop/mens-pants-jeans-shorts"],
    "acc_etc": [f"{BASE_URL}/shop/luggage-bags-packs"],
}

class PatagoniaCrawler(BaseCrawler):
    def __init__(self): super().__init__("patagonia")
    async def get_product_list_urls(self, season=None): return [u for urls in CATEGORIES.values() for u in urls]
    def get_card_selector(self): return "[class*=card]"
    def _url_to_category(self, url):
        for c, urls in CATEGORIES.items():
            for u in urls:
                if u == url: return c
        return None

    async def crawl(self, season=None, max_pages=10, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth
        products, seen = [], set()
        stealth = Stealth()
        async with async_playwright() as pw:
            stealth.hook_playwright_context(pw)
            browser = await pw.chromium.launch(headless=True)
            page = await (await browser.new_context(viewport={"width":1440,"height":900}, locale="ko-KR")).new_page()
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
                            const cards = document.querySelectorAll('[class*="card"]');
                            const seen = new Set();
                            return Array.from(cards).map(card => {
                                const link = card.querySelector('a[href*="/product/"]') || card.querySelector('a[href]');
                                if (!link) return null;
                                const href = link.href || '';
                                if (!href.includes('/product/') && !href.includes('/shop/')) return null;
                                const slug = href.split('/').pop().split('?')[0];
                                if (!slug || seen.has(slug)) return null;
                                seen.add(slug);
                                const img = card.querySelector('img');
                                const text = card.innerText.trim();
                                const lines = text.split('\\n').map(l=>l.trim()).filter(l=>l.length>1);
                                let name='', price='';
                                for (const l of lines) {
                                    if (l.match(/₩|원|\\d{2,3},\\d{3}/)) {price=l; continue;}
                                    if (!name && l.length > 2) name = l;
                                }
                                return {slug, href, name: name||slug, price, img: img?(img.src||''):''};
                            }).filter(x=>x);
                        }""")
                        for item in items:
                            pid = self.make_product_id(item["slug"][:40])
                            if pid in seen: continue
                            seen.add(pid)
                            ps = re.sub(r"[^\d]", "", item.get("price","").split("~")[0])
                            raw = {"id":pid,"product_name":item["name"],"product_name_kr":item["name"],
                                "price":int(ps) if ps else 0,"sale_price":None,"currency":"KRW",
                                "category_id":cat,"season_id":"2026SS","colors":[],
                                "thumbnail_url":item["img"],"image_urls":[item["img"]] if item["img"] else [],
                                "product_url":item["href"],
                                "style_tags":["outdoor","sustainable"]}
                            products.append(self.normalize_product(raw))
                        self.logger.info(f"Found {len(items)}, total unique: {len(products)}")
                        await asyncio.sleep(2)
                    except Exception as e: self.logger.error(f"Failed: {url} - {e}")
            finally: await browser.close()
        self.logger.info(f"Total: {len(products)}")
        return products

    async def parse_product_card(self, page, element): return None
