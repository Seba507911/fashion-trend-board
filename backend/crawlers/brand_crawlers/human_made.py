"""Human Made 크롤러. Shopify JP, [class*=tile] 기반."""
from __future__ import annotations
import asyncio, re
from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://humanmade.jp"
CATEGORIES = {
    "outer": [f"{BASE_URL}/collections/outerwear"],
    "inner": [f"{BASE_URL}/collections/tops", f"{BASE_URL}/collections/knit"],
    "bottom": [f"{BASE_URL}/collections/bottoms"],
    "headwear": [f"{BASE_URL}/collections/headwear"],
    "bag": [f"{BASE_URL}/collections/bags"],
    "acc_etc": [f"{BASE_URL}/collections/accessories"],
}

class HumanMadeCrawler(BaseCrawler):
    def __init__(self): super().__init__("human_made")
    async def get_product_list_urls(self, season=None): return [u for urls in CATEGORIES.values() for u in urls]
    def get_card_selector(self): return "[class*=tile]"
    def _url_to_category(self, url):
        for c, urls in CATEGORIES.items():
            for u in urls:
                if u == url: return c
        return None

    async def crawl(self, season=None, max_pages=10, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright
        products, seen = [], set()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await (await browser.new_context(user_agent="Mozilla/5.0", viewport={"width":1440,"height":900}, locale="ja-JP")).new_page()
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
                            const tiles = document.querySelectorAll('[class*="tile"]');
                            const seen = new Set();
                            return Array.from(tiles).map(tile => {
                                const link = tile.querySelector('a[href*="/products/"]');
                                if (!link) return null;
                                const href = link.getAttribute('href') || '';
                                const slug = href.split('/products/')[1]?.split('?')[0];
                                if (!slug || seen.has(slug)) return null;
                                seen.add(slug);
                                const img = tile.querySelector('img');
                                const text = tile.innerText.trim();
                                const lines = text.split('\\n').map(l=>l.trim()).filter(l=>l.length>1);
                                let name='', price='';
                                for (const l of lines) {
                                    if (l.match(/¥|円|\\d{2,3},\\d{3}/)) {price=l; continue;}
                                    if (l === 'SOLD OUT' || l === 'NEW') continue;
                                    if (!name && l.length > 2) name = l;
                                }
                                return {slug, href, name: name||slug, price, img: img?(img.src||''):''};
                            }).filter(x=>x);
                        }""")
                        for item in items:
                            pid = self.make_product_id(item["slug"][:40])
                            if pid in seen: continue
                            seen.add(pid)
                            ps = re.sub(r"[^\d]", "", item.get("price",""))
                            raw = {"id":pid,"product_name":item["name"],"product_name_kr":item["name"],
                                "price":int(ps) if ps else 0,"sale_price":None,"currency":"JPY",
                                "category_id":cat,"season_id":"2026SS","colors":[],
                                "thumbnail_url":item["img"],"image_urls":[item["img"]] if item["img"] else [],
                                "product_url":BASE_URL+item["href"] if not item["href"].startswith("http") else item["href"],
                                "style_tags":["japanese","street","graphic"]}
                            products.append(self.normalize_product(raw))
                        self.logger.info(f"Found {len(items)}, total unique: {len(products)}")
                        await asyncio.sleep(2)
                    except Exception as e: self.logger.error(f"Failed: {url} - {e}")
            finally: await browser.close()
        self.logger.info(f"Total: {len(products)}")
        return products

    async def parse_product_card(self, page, element): return None
