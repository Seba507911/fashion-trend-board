"""Nanushka 크롤러. Shopify 기반, a[href*="/products/"] 파싱."""
from __future__ import annotations
import asyncio, re
from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://nanushka.com"
CATEGORIES = {
    "outer": [f"{BASE_URL}/collections/outerwear"],
    "inner": [f"{BASE_URL}/collections/tops", f"{BASE_URL}/collections/knitwear", f"{BASE_URL}/collections/shirts"],
    "bottom": [f"{BASE_URL}/collections/trousers", f"{BASE_URL}/collections/shorts", f"{BASE_URL}/collections/denim"],
    "wear_etc": [f"{BASE_URL}/collections/dresses"],
    "bag": [f"{BASE_URL}/collections/bags"],
    "shoes": [f"{BASE_URL}/collections/shoes"],
    "acc_etc": [f"{BASE_URL}/collections/all-accessories"],
}

class NanushkaCrawler(BaseCrawler):
    def __init__(self): super().__init__("nanushka")
    async def get_product_list_urls(self, season=None): return [u for urls in CATEGORIES.values() for u in urls]
    def get_card_selector(self): return "a[href*='/products/']"
    def _url_to_category(self, url):
        for c, urls in CATEGORIES.items():
            for u in urls:
                if u == url: return c
        return None

    async def crawl(self, season=None, max_pages=12, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright
        products, seen = [], set()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await (await browser.new_context(user_agent="Mozilla/5.0", viewport={"width":1440,"height":900})).new_page()
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
                            const links = document.querySelectorAll('a[href*="/products/"]');
                            const seen = new Set();
                            return Array.from(links).map(a => {
                                const href = a.getAttribute('href') || '';
                                const slug = href.split('/products/')[1]?.split('?')[0];
                                if (!slug || seen.has(slug)) return null;
                                seen.add(slug);
                                const img = a.querySelector('img');
                                const text = a.innerText.trim();
                                const lines = text.split('\\n').map(l=>l.trim()).filter(l=>l.length>1);
                                let name='', price='';
                                for (const l of lines) {
                                    if (l.match(/^[€$₩¥£]/) || l.match(/\\d.*[€$₩¥£]/)) {price=l; continue;}
                                    if (!name && l.length > 2) name = l;
                                }
                                return {slug, href, name: name||slug, price, img: img?(img.src||''):''};
                            }).filter(x=>x);
                        }""")
                        for item in items:
                            pid = self.make_product_id(item["slug"][:40])
                            if pid in seen: continue
                            seen.add(pid)
                            ps = re.sub(r"[^\d.]", "", item.get("price","").split("-")[0])
                            raw = {"id":pid,"product_name":item["name"],"product_name_kr":item["name"],
                                "price":int(float(ps)) if ps else 0,"sale_price":None,"currency":"USD",
                                "category_id":cat,"season_id":"2026SS","colors":[],
                                "thumbnail_url":item["img"],"image_urls":[item["img"]] if item["img"] else [],
                                "product_url":BASE_URL+item["href"] if not item["href"].startswith("http") else item["href"],
                                "style_tags":["sustainable","contemporary","luxury"]}
                            products.append(self.normalize_product(raw))
                        self.logger.info(f"Found {len(items)}, total unique: {len(products)}")
                        await asyncio.sleep(2)
                    except Exception as e: self.logger.error(f"Failed: {url} - {e}")
            finally: await browser.close()
        self.logger.info(f"Total: {len(products)}")
        return products

    async def parse_product_card(self, page, element): return None
