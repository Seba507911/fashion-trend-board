"""Ami Paris 크롤러. Shopify /products.json API."""
from __future__ import annotations
import re, time, requests
from html import unescape
from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.amiparis.com"

# French title keywords → category mapping
OUTER_KW = ("veste", "manteau", "blouson", "parka", "trench", "doudoune", "cape", "coat", "jacket")
INNER_KW = ("chemise", "polo", "pull", "cardigan", "t-shirt", "tee-shirt", "sweat", "top", "maille",
            "débardeur", "gilet", "shirt", "sweater", "hoodie", "knit")
BOTTOM_KW = ("pantalon", "jean", "short", "bermuda", "jupe", "trouser", "pant", "skirt", "denim")
DRESS_KW = ("robe", "combinaison", "dress", "jumpsuit")
BAG_KW = ("sac", "pochette", "bag", "tote", "clutch")
SHOE_KW = ("sneaker", "derby", "mocassin", "botte", "sandale", "espadrille", "shoe", "boot", "loafer", "mule")
ACC_KW = ("ceinture", "écharpe", "foulard", "chapeau", "bob", "casquette", "bonnet", "bijou",
          "collier", "bracelet", "bague", "porte-clé", "belt", "scarf", "hat", "cap", "wallet")


class AmiParisCrawler(BaseCrawler):
    def __init__(self): super().__init__("ami")
    async def get_product_list_urls(self, season=None): return []
    def get_card_selector(self): return ""

    def _strip_html(self, html):
        if not html: return ""
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(html))).strip()[:500]

    def _category(self, title):
        t = (title or "").lower()
        if any(k in t for k in OUTER_KW): return "outer"
        if any(k in t for k in INNER_KW): return "inner"
        if any(k in t for k in BOTTOM_KW): return "bottom"
        if any(k in t for k in DRESS_KW): return "wear_etc"
        if any(k in t for k in BAG_KW): return "bag"
        if any(k in t for k in SHOE_KW): return "shoes"
        if any(k in t for k in ACC_KW): return "acc_etc"
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
                title = p.get("title","")
                desc = self._strip_html(p.get("body_html",""))
                materials = re.findall(r"\d+%\s*[A-Za-zÀ-ÿ]+|[A-Za-zÀ-ÿ]+\s*\d+%", desc)
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
                raw = {"id":pid,"product_name":title,"product_name_kr":title,
                    "price":price,"sale_price":None,"currency":"EUR",
                    "category_id":self._category(title),
                    "season_id":"2026SS","colors":list(colors),"materials":materials[:5],
                    "sizes":sizes,"description":desc,
                    "thumbnail_url":img,"image_urls":[i.get("src","") for i in images[:5]],
                    "product_url":f"{BASE_URL}/products/{handle}",
                    "style_tags":["french","contemporary","ami-de-coeur"]}
                products.append(self.normalize_product(raw))
            self.logger.info(f"Page {page}: {len(data)}, total: {len(products)}")
            page += 1; time.sleep(1)
        self.logger.info(f"Total: {len(products)}")
        return products
    async def parse_product_card(self, page, element): return None
