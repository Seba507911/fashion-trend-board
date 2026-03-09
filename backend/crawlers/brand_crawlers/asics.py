"""ASICS Korea 공식몰 크롤러.

대상: https://www.asics.com/kr/ko-kr/
카테고리 URL 패턴: /kr/ko-kr/{category}.html
"""
import re
from typing import Optional

from playwright.async_api import Page

from backend.crawlers.base_crawler import BaseCrawler

CATEGORY_MAP = {
    "mens-shoes": "sneakers",
    "mens-clothing": "top",
    "womens-shoes": "sneakers",
    "womens-clothing": "top",
}

BASE_URL = "https://www.asics.com/kr/ko-kr"


class AsicsCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("asics")

    async def get_product_list_urls(self, season: Optional[str] = None) -> list[str]:
        return [
            f"{BASE_URL}/mens-shoes.html",
            f"{BASE_URL}/mens-clothing.html",
            f"{BASE_URL}/womens-shoes.html",
            f"{BASE_URL}/womens-clothing.html",
        ]

    def get_card_selector(self) -> str:
        return ".product-tile"

    async def parse_product_card(self, page: Page, element) -> Optional[dict]:
        try:
            name_el = await element.query_selector(".product-tile__name, .product-name")
            price_el = await element.query_selector(".product-tile__price, .price-sales")
            img_el = await element.query_selector("img")
            link_el = await element.query_selector("a")

            name = await name_el.inner_text() if name_el else None
            if not name:
                return None

            price_text = await price_el.inner_text() if price_el else "0"
            price = int(re.sub(r"[^\d]", "", price_text) or 0)

            img_url = await img_el.get_attribute("src") if img_el else None
            link = await link_el.get_attribute("href") if link_el else None
            product_url = f"{BASE_URL}{link}" if link and not link.startswith("http") else link

            # 상품 코드 추출 시도
            code = ""
            if link:
                match = re.search(r"/([A-Z0-9]+-[A-Z0-9]+)", link)
                if match:
                    code = match.group(1)
                else:
                    code = re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

            return {
                "id": self.make_product_id(code),
                "product_name": name.strip(),
                "product_name_kr": name.strip(),
                "price": price,
                "thumbnail_url": img_url,
                "image_urls": [img_url] if img_url else [],
                "product_url": product_url,
                "style_tags": ["athletic", "performance"],
            }
        except Exception as e:
            self.logger.warning(f"ASICS parse error: {e}")
            return None
