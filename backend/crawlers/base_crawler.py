"""크롤러 베이스 클래스."""
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from playwright.async_api import async_playwright, Page  # noqa: F401


class BaseCrawler(ABC):
    """모든 브랜드 크롤러의 베이스 클래스."""

    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        self.logger = logging.getLogger(f"crawler.{brand_id}")

    @abstractmethod
    async def get_product_list_urls(self, season: Optional[str] = None) -> list[str]:
        """상품 목록 페이지 URL 생성."""

    @abstractmethod
    async def parse_product_card(self, page: Page, element) -> Optional[dict]:
        """목록 페이지의 상품 카드 하나를 파싱."""

    @abstractmethod
    def get_card_selector(self) -> str:
        """상품 카드 CSS 셀렉터."""

    def make_product_id(self, product_code: str) -> str:
        """상품 ID 생성."""
        return f"{self.brand_id}_{product_code}"

    def normalize_product(self, raw: dict) -> dict:
        """크롤링 결과를 DB 스키마에 맞게 정규화."""
        return {
            "id": raw.get("id", ""),
            "brand_id": self.brand_id,
            "season_id": raw.get("season_id"),
            "category_id": raw.get("category_id"),
            "product_name": raw.get("product_name", ""),
            "product_name_kr": raw.get("product_name_kr"),
            "price": raw.get("price"),
            "sale_price": raw.get("sale_price"),
            "currency": raw.get("currency", "KRW"),
            "colors": json.dumps(raw.get("colors", []), ensure_ascii=False),
            "materials": json.dumps(raw.get("materials", []), ensure_ascii=False),
            "image_urls": json.dumps(raw.get("image_urls", []), ensure_ascii=False),
            "thumbnail_url": raw.get("thumbnail_url"),
            "product_url": raw.get("product_url"),
            "style_tags": json.dumps(raw.get("style_tags", []), ensure_ascii=False),
            "sizes": json.dumps(raw.get("sizes", []), ensure_ascii=False),
            "fit_info": raw.get("fit_info"),
            "description": raw.get("description"),
            "is_active": 1,
            "crawled_at": datetime.now().isoformat(),
        }

    async def parse_product_detail(self, page: Page, url: str) -> dict:
        """상품 상세 페이지에서 추가 정보 추출 (서브클래스에서 오버라이드)."""
        return {}

    async def crawl(
        self, season: Optional[str] = None, max_pages: int = 5,
        dry_run: bool = False, fetch_details: bool = False
    ) -> list[dict]:
        """전체 크롤링 실행.

        Args:
            fetch_details: True면 각 상품의 상세 페이지도 크롤링하여 추가 정보 수집
        """
        products = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1440, "height": 900},
            )
            page = await context.new_page()

            try:
                urls = await self.get_product_list_urls(season)
                for i, url in enumerate(urls[:max_pages]):
                    self.logger.info(f"Crawling page {i + 1}/{len(urls)}: {url}")
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        await asyncio.sleep(5)
                        # 스크롤 다운하여 lazy load 트리거
                        await page.evaluate("window.scrollTo(0, 1000)")
                        await asyncio.sleep(2)

                        cards = await page.query_selector_all(self.get_card_selector())
                        self.logger.info(f"Found {len(cards)} product cards")

                        for card in cards:
                            try:
                                raw = await self.parse_product_card(page, card)
                                if raw:
                                    product = self.normalize_product(raw)
                                    products.append(product)
                                    if dry_run:
                                        self.logger.info(f"  [DRY] {product['product_name']} - {product['price']} {product.get('currency', '')}")
                            except Exception as e:
                                self.logger.warning(f"Card parse failed: {e}")
                                continue

                        await asyncio.sleep(2)
                    except Exception as e:
                        self.logger.error(f"Page crawl failed: {url} - {e}")
                        continue

                # 상세 페이지 크롤링 (옵션)
                if fetch_details and not dry_run:
                    self.logger.info(f"Fetching details for {len(products)} products...")
                    for i, product in enumerate(products):
                        purl = product.get("product_url")
                        if not purl:
                            continue
                        try:
                            detail = await self.parse_product_detail(page, purl)
                            if detail.get("colors"):
                                product["colors"] = json.dumps(detail["colors"], ensure_ascii=False)
                            if detail.get("sizes"):
                                product["sizes"] = json.dumps(detail["sizes"], ensure_ascii=False)
                            if detail.get("materials"):
                                product["materials"] = json.dumps(detail["materials"], ensure_ascii=False)
                            if detail.get("fit_info"):
                                product["fit_info"] = detail["fit_info"]
                            if detail.get("description"):
                                product["description"] = detail["description"]
                            self.logger.info(f"  [{i+1}/{len(products)}] {product['product_name']} - sizes:{len(detail.get('sizes', []))} colors:{len(detail.get('colors', []))}")
                            await asyncio.sleep(2)
                        except Exception as e:
                            self.logger.warning(f"Detail fetch failed: {e}")
                            continue
            finally:
                await browser.close()

        self.logger.info(f"Total crawled: {len(products)} products")
        return products
