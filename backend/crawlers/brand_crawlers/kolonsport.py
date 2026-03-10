"""코오롱스포츠 공식몰 크롤러.

대상: https://www.kolonsport.com (Next.js + Apollo GraphQL)
카테고리: /Category/List/{categoryId}?productGenders=MALE|FEMALE
상품 데이터: __NEXT_DATA__ script 태그 내 apolloState에서 추출
상세 URL: /Product/{code}

WAF 없음 — requests + BeautifulSoup 기반 (Playwright 불필요).
페이지네이션은 누적 방식: page=N 요청 시 1~N 페이지 전체 결과 반환.
상품코드 뒤 3글자가 컬러코드(e.g., BLK, GKH) → 잘라서 base code로 dedup.
"""
from __future__ import annotations

import asyncio
import json
import math
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.kolonsport.com"
PAGE_SIZE = 60  # 서버 고정값

# 카테고리 ID 매핑
CATEGORY_IDS = {
    "outer": "105010080100",
    "top": "105010080200",
    "bottom": "105010080300",
    "shoes": "105010090000",
    "bag": "105010100000",
}

GENDERS = ["MALE", "FEMALE"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


def _strip_color_suffix(code: str) -> str:
    """상품코드에서 뒤 3글자 컬러 접미사 제거.

    예: TLJJM26591BLK → TLJJM26591
        JWVAM26301NAY → JWVAM26301
    코드는 보통 영문+숫자 10자리 + 컬러 3자리.
    """
    if len(code) > 3 and re.match(r"^[A-Z0-9]+$", code):
        return code[:-3]
    return code


class KolonSportCrawler(BaseCrawler):
    """코오롱스포츠 크롤러 (requests 기반)."""

    def __init__(self):
        super().__init__("kolonsport")
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    # ── BaseCrawler abstract 메서드 (사용하지 않지만 구현 필요) ──

    async def get_product_list_urls(self, season: Optional[str] = None) -> list[str]:
        """사용하지 않음 — crawl()에서 직접 URL 생성."""
        return []

    async def parse_product_card(self, page, element) -> Optional[dict]:
        """사용하지 않음 — _parse_apollo_products()로 대체."""
        return None

    def get_card_selector(self) -> str:
        """사용하지 않음."""
        return ""

    # ── 핵심 로직 ──

    def _build_url(
        self, category_id: str, gender: str, page: int = 1
    ) -> str:
        """카테고리 목록 URL 생성."""
        return (
            f"{BASE_URL}/Category/List/{category_id}"
            f"?productGenders={gender}&sort=newProduct-desc&page={page}&pageSize={PAGE_SIZE}"
        )

    def _fetch_apollo_state(self, url: str) -> Optional[dict]:
        """URL에서 __NEXT_DATA__ → apolloState 추출."""
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {url} - {e}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        script_el = soup.find("script", id="__NEXT_DATA__")
        if not script_el or not script_el.string:
            self.logger.warning(f"No __NEXT_DATA__ found: {url}")
            return None

        try:
            data = json.loads(script_el.string)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse failed: {e}")
            return None

        return data.get("props", {}).get("apolloState", {})

    def _extract_products_from_apollo(
        self, apollo: dict, category_id: str, gender: str
    ) -> tuple[list[dict], int]:
        """apolloState의 ROOT_QUERY에서 상품 리스트와 totalCount 추출.

        Returns:
            (상품 리스트, totalCount)
        """
        root = apollo.get("ROOT_QUERY", {})

        # products:{...} 키 중 해당 카테고리+젠더에 매칭되는 것 찾기
        target_key = None
        for key in root:
            if not key.startswith("products:"):
                continue
            if f'"categoryId":"{category_id}"' in key and f'"productGender":"{gender}"' in key:
                target_key = key
                break

        if target_key is None:
            return [], 0

        products_data = root[target_key]
        if products_data is None:
            return [], 0

        results = products_data.get("results", [])
        total_count = products_data.get("page", {}).get("totalCount", 0)
        return results, total_count

    def _parse_product(self, raw: dict, category_id: str, gender: str) -> Optional[dict]:
        """Apollo 상품 데이터 → 정규화된 dict."""
        code = raw.get("code", "")
        name = raw.get("name", "")
        if not code or not name:
            return None

        base_code = _strip_color_suffix(code)

        # 가격
        price_data = raw.get("price", {}) or {}
        price = price_data.get("price", 0)
        discount_rate = price_data.get("discountRate", 0)
        sale_price = None
        if discount_rate and discount_rate > 0:
            # formattedWishPrice가 할인가
            wish_str = price_data.get("formattedWishPrice", "")
            wish_val = int(re.sub(r"[^\d]", "", wish_str) or 0)
            if 0 < wish_val < price:
                sale_price = wish_val

        # 컬러: colorImagesEx 배열에서 추출
        color_images = raw.get("colorImagesEx", []) or []
        colors = list(dict.fromkeys(
            ci.get("name", "") for ci in color_images if ci.get("name")
        ))

        # 이미지
        represent_images = raw.get("representImages", []) or []
        thumbnail = raw.get("representationImage", "")
        image_urls = represent_images[:7] if represent_images else []
        if not image_urls and thumbnail:
            image_urls = [thumbnail]

        # 상품 URL
        product_url = f"{BASE_URL}/Product/{code}"

        # 카테고리 매핑
        cat_name = None
        for cname, cid in CATEGORY_IDS.items():
            if cid == category_id:
                cat_name = cname
                break

        # 성별 태그
        gender_tag = "men" if gender == "MALE" else "women"

        # sellingPoint에서 시즌 추출
        selling_point = raw.get("sellingPoint", "") or ""
        season_id = "2026SS"
        if "26FW" in selling_point or "25FW" in selling_point:
            season_id = "2026FW" if "26FW" in selling_point else "2025FW"
        elif "25SS" in selling_point:
            season_id = "2025SS"

        return {
            "id": self.make_product_id(base_code),
            "product_name": name,
            "product_name_kr": name,
            "price": price,
            "sale_price": sale_price,
            "currency": "KRW",
            "category_id": cat_name,
            "season_id": season_id,
            "colors": colors,
            "sizes": [],
            "thumbnail_url": thumbnail,
            "image_urls": image_urls,
            "product_url": product_url,
            "style_tags": ["outdoor", "sportswear", gender_tag],
        }

    async def crawl(
        self,
        season: Optional[str] = None,
        max_pages: int = 50,
        dry_run: bool = False,
        fetch_details: bool = False,
    ) -> list[dict]:
        """전체 크롤링 실행 (Playwright 없이 requests 사용).

        누적 페이지네이션 활용: 마지막 페이지를 요청하면 전체 결과가 포함됨.
        전략: 1페이지로 totalCount 파악 → 마지막 페이지 한 번 요청으로 전체 수집.
        """
        products: list[dict] = []
        seen_base_codes: set[str] = set()

        for cat_name, cat_id in CATEGORY_IDS.items():
            for gender in GENDERS:
                self.logger.info(
                    f"Crawling {cat_name} / {gender} (category={cat_id})"
                )

                # 1단계: 1페이지에서 totalCount 확인
                url_page1 = self._build_url(cat_id, gender, page=1)
                apollo = self._fetch_apollo_state(url_page1)
                if not apollo:
                    continue

                results, total_count = self._extract_products_from_apollo(
                    apollo, cat_id, gender
                )
                self.logger.info(
                    f"  Page 1: {len(results)} items, total={total_count}"
                )

                if total_count == 0:
                    continue

                # 2단계: 마지막 페이지 요청 (누적이므로 전체 포함)
                last_page = math.ceil(total_count / PAGE_SIZE)
                if last_page > 1:
                    await asyncio.sleep(2.5)
                    url_last = self._build_url(cat_id, gender, page=last_page)
                    apollo_last = self._fetch_apollo_state(url_last)
                    if apollo_last:
                        results, _ = self._extract_products_from_apollo(
                            apollo_last, cat_id, gender
                        )
                        self.logger.info(
                            f"  Page {last_page} (last): {len(results)} items"
                        )

                # 3단계: 파싱 & dedup
                cat_count = 0
                for raw in results:
                    if raw is None:
                        continue
                    parsed = self._parse_product(raw, cat_id, gender)
                    if not parsed:
                        continue

                    base_code = _strip_color_suffix(raw.get("code", ""))
                    if base_code in seen_base_codes:
                        continue
                    seen_base_codes.add(base_code)

                    product = self.normalize_product(parsed)
                    products.append(product)
                    cat_count += 1

                    if dry_run:
                        self.logger.info(
                            f"  [DRY] {product['product_name']} "
                            f"({base_code}) - {product['price']} KRW "
                            f"colors={parsed['colors']}"
                        )

                self.logger.info(
                    f"  → {cat_name}/{gender}: {cat_count} unique products"
                )

                # 카테고리 간 딜레이
                await asyncio.sleep(2.5)

        self.logger.info(f"Total crawled: {len(products)} unique products")
        return products
