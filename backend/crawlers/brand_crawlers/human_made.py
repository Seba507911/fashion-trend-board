"""Human Made 크롤러. Shopify /products.json API 직접 호출."""
from __future__ import annotations
import json, re, time, requests
from backend.crawlers.base_crawler import BaseCrawler
from html import unescape

BASE_URL = "https://humanmade.jp"

class HumanMadeCrawler(BaseCrawler):
    def __init__(self): super().__init__("human_made")
    async def get_product_list_urls(self, season=None): return []
    def get_card_selector(self): return ""

    def _strip_html(self, html):
        if not html: return ""
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(html))).strip()[:500]

    def _category_from_type(self, ptype, tags):
        pt = (ptype or "").lower()
        t = set(tag.lower() for tag in (tags or []))
        if pt in ("outerwear","jackets","coats") or t & {"outerwear"}: return "outer"
        if pt in ("tops","t-shirts","shirts","knitwear","knit","sweatshirts") or t & {"tops","knit"}: return "inner"
        if pt in ("bottoms","pants","shorts","trousers") or t & {"bottoms"}: return "bottom"
        if pt in ("headwear","caps","hats") or t & {"headwear"}: return "headwear"
        if pt in ("bags",) or t & {"bags"}: return "bag"
        if pt in ("accessories",) or t & {"accessories"}: return "acc_etc"
        return None

    async def crawl(self, season=None, max_pages=10, dry_run=False, fetch_details=False):
        products, seen = [], set()
        page = 1
        while page <= max_pages:
            url = f"{BASE_URL}/products.json?limit=250&page={page}"
            self.logger.info(f"Fetching page {page}: {url}")
            try:
                resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
                data = resp.json().get("products", [])
            except Exception as e:
                self.logger.error(f"API error: {e}")
                break
            if not data: break

            for p in data:
                handle = p.get("handle", "")
                pid = self.make_product_id(handle[:40])
                if pid in seen: continue
                seen.add(pid)

                name = p.get("title", "")
                desc = self._strip_html(p.get("body_html", ""))
                ptype = p.get("product_type", "")
                tags = p.get("tags", [])
                cat = self._category_from_type(ptype, tags)
                materials = re.findall(r"\d+%\s*[A-Za-z]+|[A-Za-z]+\s*\d+%", desc)

                variants = p.get("variants", [])
                price = 0; sizes = []; colors = set()
                for v in variants:
                    vp = float(v.get("price", 0) or 0)
                    if vp > 0 and price == 0: price = int(vp)
                    o1 = v.get("option1", ""); o2 = v.get("option2", "")
                    if o1 and o1 not in sizes: sizes.append(o1)
                    if o2: colors.add(o2)

                images = p.get("images", [])
                img = images[0].get("src", "") if images else ""

                raw = {
                    "id": pid, "product_name": name, "product_name_kr": name,
                    "price": price, "sale_price": None, "currency": "JPY",
                    "category_id": cat, "season_id": "2026SS",
                    "colors": list(colors), "materials": materials[:5],
                    "sizes": sizes, "description": desc,
                    "thumbnail_url": img, "image_urls": [i.get("src","") for i in images[:5]],
                    "product_url": f"{BASE_URL}/products/{handle}",
                    "style_tags": ["japanese", "street", "graphic"],
                }
                products.append(self.normalize_product(raw))

            self.logger.info(f"Page {page}: {len(data)} products, total unique: {len(products)}")
            page += 1
            time.sleep(1)

        self.logger.info(f"Total: {len(products)}")
        return products

    async def parse_product_card(self, page, element): return None
