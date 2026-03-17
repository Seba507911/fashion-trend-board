"""Zara Korea 크롤러.

대상: https://www.zara.com/kr/ko/
Stealth Playwright + API 인터셉트 방식.
카테고리 페이지 로드 시 /category/{id}/products?ajax=true API를
자동 호출하므로, 이를 캡처하여 상품 데이터를 추출.
"""
from __future__ import annotations

import asyncio
import json
from typing import Optional

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.zara.com"

# Zara 카테고리 페이지 URL (API의 categoryId는 페이지 로드 시 자동 결정)
CATEGORY_PAGES = {
    "inner": [
        f"{BASE_URL}/kr/ko/woman-shirts-l1217.html",
        f"{BASE_URL}/kr/ko/woman-tshirts-l1362.html",
        f"{BASE_URL}/kr/ko/man-tshirts-l855.html",
        f"{BASE_URL}/kr/ko/man-shirts-l737.html",
    ],
    "outer": [
        f"{BASE_URL}/kr/ko/woman-outerwear-l1184.html",
        f"{BASE_URL}/kr/ko/man-outerwear-l700.html",
    ],
    "bottom": [
        f"{BASE_URL}/kr/ko/woman-trousers-l1335.html",
        f"{BASE_URL}/kr/ko/woman-jeans-l1119.html",
        f"{BASE_URL}/kr/ko/man-trousers-l838.html",
        f"{BASE_URL}/kr/ko/man-jeans-l659.html",
    ],
    "wear_etc": [
        f"{BASE_URL}/kr/ko/woman-dresses-l1066.html",
    ],
    "shoes": [
        f"{BASE_URL}/kr/ko/woman-shoes-l1251.html",
        f"{BASE_URL}/kr/ko/man-shoes-l769.html",
    ],
    "bag": [
        f"{BASE_URL}/kr/ko/woman-bags-l1024.html",
    ],
    "acc_etc": [
        f"{BASE_URL}/kr/ko/woman-accessories-l1003.html",
        f"{BASE_URL}/kr/ko/man-accessories-l587.html",
    ],
}


class ZaraCrawler(BaseCrawler):
    """자라 코리아 크롤러 (stealth + API 인터셉트)."""

    def __init__(self):
        super().__init__("zara")

    async def get_product_list_urls(self, season=None):
        urls = []
        for cat_urls in CATEGORY_PAGES.values():
            urls.extend(cat_urls)
        return urls

    def get_card_selector(self):
        return ".product-grid-product"

    def _url_to_category(self, page_url):
        for cat_id, cat_urls in CATEGORY_PAGES.items():
            for curl in cat_urls:
                if curl == page_url:
                    return cat_id
        return None

    def _parse_api_products(self, api_data: dict) -> list[dict]:
        """API 응답에서 상품 목록 추출."""
        results = []
        product_groups = api_data.get("productGroups", [])
        for group in product_groups:
            for element in group.get("elements", []):
                for comp in element.get("commercialComponents", []):
                    if comp.get("type") != "Product":
                        continue
                    prod_id = str(comp.get("id", ""))
                    name = comp.get("name", "")
                    if not prod_id or not name:
                        continue

                    # Price
                    # Price (KRW, e.g. 55900 = ₩55,900)
                    price = 0
                    sale_price = None

                    # Image + Color — from detail.colors
                    img_url = ""
                    colors = []
                    detail = comp.get("detail", {})
                    if isinstance(detail, dict):
                        color_info = detail.get("colors", [])
                        for c in color_info:
                            cname = c.get("name", "")
                            if cname:
                                colors.append(cname)
                            # Image from color xmedia
                            if not img_url:
                                color_xmedia = c.get("xmedia", [])
                                for xm in color_xmedia:
                                    if xm.get("type") == "image":
                                        path = xm.get("path", "")
                                        name_media = xm.get("name", "")
                                        ts = xm.get("timestamp", "0")
                                        if path and name_media:
                                            img_url = f"https://static.zara.net{path}/{name_media}.jpg?ts={ts}&w=750"
                                            break
                            # Price from color (more reliable)
                            if not price:
                                cprice = c.get("price", 0)
                                if isinstance(cprice, (int, float)):
                                    price = int(cprice)
                                elif isinstance(cprice, dict):
                                    price = int(cprice.get("price", 0) or 0)

                    # Fallback: xmedia at component level
                    if not img_url:
                        xmedia = comp.get("xmedia", [])
                        if xmedia:
                            first_media = xmedia[0]
                            path = first_media.get("path", "")
                            name_media = first_media.get("name", "")
                            if path and name_media:
                                img_url = f"https://static.zara.net{path}/{name_media}.jpg?ts=0&w=750"

                    # URL
                    seo = comp.get("seo", {})
                    keyword = seo.get("keyword", "")
                    seo_id = seo.get("seoProductId", "")
                    product_url = f"{BASE_URL}/kr/ko/{keyword}-p{seo_id}.html" if keyword and seo_id else ""

                    results.append({
                        "id": prod_id,
                        "name": name,
                        "price": price,
                        "sale_price": sale_price,
                        "img_url": img_url,
                        "colors": colors,
                        "product_url": product_url,
                    })
        return results

    async def crawl(self, season=None, max_pages=15, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth

        products = []
        seen_ids = set()
        stealth = Stealth()

        async with async_playwright() as pw:
            stealth.hook_playwright_context(pw)
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1440, "height": 900},
                locale="ko-KR",
            )
            page = await context.new_page()

            try:
                urls = await self.get_product_list_urls(season)
                for i, url in enumerate(urls[:max_pages]):
                    self.logger.info(f"Crawling page {i + 1}/{len(urls)}: {url}")
                    category_id = self._url_to_category(url)

                    # Capture API response
                    api_data = {}

                    async def on_response(resp):
                        if "products?ajax=true" in resp.url and resp.status == 200:
                            try:
                                body = await resp.json()
                                api_data["data"] = body
                            except Exception:
                                pass

                    page.on("response", on_response)

                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        await asyncio.sleep(10)

                        page.remove_listener("response", on_response)

                        if not api_data.get("data"):
                            self.logger.warning(f"No API data captured for {url}")
                            continue

                        parsed = self._parse_api_products(api_data["data"])
                        for item in parsed:
                            pid = self.make_product_id(item["id"])
                            if pid in seen_ids:
                                continue
                            seen_ids.add(pid)

                            raw = {
                                "id": pid,
                                "product_name": item["name"],
                                "product_name_kr": item["name"],
                                "price": item["price"],
                                "sale_price": item["sale_price"],
                                "currency": "KRW",
                                "category_id": category_id,
                                "season_id": "2026SS",
                                "colors": item["colors"],
                                "thumbnail_url": item["img_url"],
                                "image_urls": [item["img_url"]] if item["img_url"] else [],
                                "product_url": item["product_url"],
                                "style_tags": ["spa", "fast-fashion", "trend"],
                            }
                            product = self.normalize_product(raw)
                            products.append(product)

                            if dry_run:
                                self.logger.info(f"  [DRY] {product['product_name']} - {item['price']} KRW")

                        self.logger.info(f"Found {len(parsed)} items, total unique: {len(products)}")
                        await asyncio.sleep(3)

                    except Exception as e:
                        self.logger.error(f"Page crawl failed: {url} - {e}")
                        page.remove_listener("response", on_response)
                        continue
            finally:
                await browser.close()

        self.logger.info(f"Total crawled: {len(products)} products")
        return products

    async def parse_product_card(self, page, element):
        return None
