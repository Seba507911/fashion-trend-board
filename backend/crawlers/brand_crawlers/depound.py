"""DEPOUND 크롤러. Cafe24 커스텀 테마, Playwright 직접 파싱."""
from __future__ import annotations
import asyncio, re
from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://depound.com"
CATEGORIES = {
    "bag": [f"{BASE_URL}/product/list.html?cate_no=100", f"{BASE_URL}/product/list.html?cate_no=101"],
    "acc_etc": [f"{BASE_URL}/product/list.html?cate_no=117", f"{BASE_URL}/product/list.html?cate_no=131",
                f"{BASE_URL}/product/list.html?cate_no=132", f"{BASE_URL}/product/list.html?cate_no=134"],
}

class DepoundCrawler(BaseCrawler):
    def __init__(self): super().__init__("depound")
    async def get_product_list_urls(self, season=None): return [u for urls in CATEGORIES.values() for u in urls]
    def get_card_selector(self): return "li[id*=anchorBoxId]"
    def _url_to_category(self, url):
        for c, urls in CATEGORIES.items():
            for u in urls:
                if u == url: return c
        return None

    async def crawl(self, season=None, max_pages=8, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright
        products, seen = [], set()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
            page = await (await browser.new_context(viewport={"width":1440,"height":900}, ignore_https_errors=True)).new_page()
            try:
                for i, url in enumerate((await self.get_product_list_urls())[:max_pages]):
                    self.logger.info(f"Crawling {i+1}: {url}")
                    cat = self._url_to_category(url)
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                        await asyncio.sleep(5)
                        items = await page.evaluate("""() => {
                            const lis = document.querySelectorAll('li[id*="anchorBoxId"]');
                            return Array.from(lis).map(li => {
                                const id = (li.id || '').replace('anchorBoxId_', '');
                                const link = li.querySelector('a[href*="product"]');
                                const href = link ? link.getAttribute('href') : '';
                                const img = li.querySelector('img');
                                const imgSrc = img ? (img.src || img.getAttribute('data-src') || '') : '';
                                const name = img ? (img.alt || '') : '';
                                // Price from text
                                const text = li.innerText || '';
                                const priceMatch = text.match(/[\\d,]+원/);
                                const price = priceMatch ? priceMatch[0] : '';
                                return {id, href, name, price, img: imgSrc};
                            }).filter(x => x.id && x.name);
                        }""")
                        for item in items:
                            pid = self.make_product_id(item["id"])
                            if pid in seen: continue
                            seen.add(pid)
                            ps = re.sub(r"[^\d]", "", item.get("price",""))
                            img = item.get("img","")
                            if img.startswith("//"): img = "https:" + img
                            purl = item.get("href","")
                            if purl and not purl.startswith("http"): purl = BASE_URL + purl
                            raw = {
                                "id": pid, "product_name": item["name"], "product_name_kr": item["name"],
                                "price": int(ps) if ps else 0, "sale_price": None, "currency": "KRW",
                                "category_id": cat, "season_id": "2026SS", "colors": [],
                                "thumbnail_url": img, "image_urls": [img] if img else [],
                                "product_url": purl,
                                "style_tags": ["minimal", "accessories", "bag"],
                            }
                            products.append(self.normalize_product(raw))
                        self.logger.info(f"Found {len(items)}, total unique: {len(products)}")
                        await asyncio.sleep(2)
                    except Exception as e: self.logger.error(f"Failed: {url} - {e}")
            finally: await browser.close()
        self.logger.info(f"Total: {len(products)}")
        return products

    async def parse_product_card(self, page, element): return None
