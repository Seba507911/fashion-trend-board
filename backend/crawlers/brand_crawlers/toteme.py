"""Totême 크롤러. Shopify /products.json API."""
from __future__ import annotations
import re, time, requests
from html import unescape
from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.toteme-studio.com"

class TotemeCrawler(BaseCrawler):
    def __init__(self): super().__init__("toteme")
    async def get_product_list_urls(self, season=None): return []
    def get_card_selector(self): return ""

    def _strip_html(self, html):
        if not html: return ""
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(html))).strip()[:500]

    def _category(self, ptype):
        pt = (ptype or "").lower()
        if pt in ("outerwear","coat","jacket","blazer"): return "outer"
        if pt in ("jersey","top","shirt","knitwear","knit","sweater","t-shirt","blouse"): return "inner"
        if pt in ("trouser","pant","skirt","short","denim","jean"): return "bottom"
        if pt in ("dress",): return "wear_etc"
        if pt in ("bag","bags"): return "bag"
        if pt in ("shoe","shoes","boot","sandal"): return "shoes"
        return "acc_etc"

    async def crawl(self, season=None, max_pages=5, dry_run=False, fetch_details=False):
        products, seen = [], set()
        page = 1
        while page <= max_pages:
            url = f"{BASE_URL}/products.json?limit=250&page={page}"
            self.logger.info(f"Fetching page {page}")
            try:
                resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
                data = resp.json().get("products", [])
            except Exception as e:
                self.logger.error(f"API error: {e}"); break
            if not data: break
            for p in data:
                handle = p.get("handle","")
                pid = self.make_product_id(handle[:40])
                if pid in seen: continue
                seen.add(pid)
                desc = self._strip_html(p.get("body_html",""))
                materials = re.findall(r"\d+%\s*[A-Za-z]+|[A-Za-z]+\s*\d+%", desc)
                variants = p.get("variants",[])
                price=0; sizes=[]; colors=set()
                for v in variants:
                    vp=float(v.get("price",0) or 0)
                    if vp>0 and price==0: price=int(vp)
                    o1=v.get("option1",""); o2=v.get("option2","")
                    if o1 and o1 not in sizes: sizes.append(o1)
                    if o2: colors.add(o2)
                images = p.get("images",[])
                img = images[0].get("src","") if images else ""
                raw = {"id":pid,"product_name":p.get("title",""),"product_name_kr":p.get("title",""),
                    "price":price,"sale_price":None,"currency":"EUR",
                    "category_id":self._category(p.get("product_type","")),
                    "season_id":"2026SS","colors":list(colors),"materials":materials[:5],
                    "sizes":sizes,"description":desc,
                    "thumbnail_url":img,"image_urls":[i.get("src","") for i in images[:5]],
                    "product_url":f"{BASE_URL}/products/{handle}",
                    "style_tags":["scandi","minimal","contemporary"]}
                products.append(self.normalize_product(raw))
            self.logger.info(f"Page {page}: {len(data)}, total: {len(products)}")
            page += 1; time.sleep(1)
        self.logger.info(f"Total: {len(products)}")
        return products
    async def parse_product_card(self, page, element): return None
