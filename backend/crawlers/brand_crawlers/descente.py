"""Descente Korea 공식몰 크롤러.

대상: https://dk-on.com/DESCENTE
카테고리: /DESCENTE/category/{categoryCode}
상품 카드: .grid-item.thumb-prod (서버 렌더링 + AJAX 페이지네이션)
상세 URL: /DESCENTE/product/{productCode}/{colorCode}
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from playwright.async_api import Page

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://dk-on.com"

# categoryCode → 카테고리 매핑
CATEGORY_URLS = {
    "outer": [
        f"{BASE_URL}/DESCENTE/category/201101189",  # MEN Jackets
        f"{BASE_URL}/DESCENTE/category/202101189",  # WOMEN Jackets
    ],
    "top": [
        f"{BASE_URL}/DESCENTE/category/201101005",  # MEN Long Sleeves
        f"{BASE_URL}/DESCENTE/category/201101104",  # MEN T-shirts
        f"{BASE_URL}/DESCENTE/category/202101005",  # WOMEN Long Sleeves
        f"{BASE_URL}/DESCENTE/category/202101104",  # WOMEN T-shirts
    ],
    "bottom": [
        f"{BASE_URL}/DESCENTE/category/201101015",  # MEN Pants
        f"{BASE_URL}/DESCENTE/category/202101015",  # WOMEN Pants
    ],
    "shoes": [
        f"{BASE_URL}/DESCENTE/category/201102016",  # MEN Running Shoes
        f"{BASE_URL}/DESCENTE/category/201102197",  # MEN Lifestyle Shoes
        f"{BASE_URL}/DESCENTE/category/202102016",  # WOMEN Running Shoes
    ],
}


class DescenteCrawler(BaseCrawler):
    """데상트 코리아 크롤러."""

    def __init__(self):
        super().__init__("descente")

    async def get_product_list_urls(self, season: Optional[str] = None) -> list[str]:
        urls = []
        for cat_urls in CATEGORY_URLS.values():
            urls.extend(cat_urls)
        return urls

    def get_card_selector(self) -> str:
        return ".grid-item.thumb-prod"

    def _url_to_category(self, page_url: str) -> Optional[str]:
        for cat_id, cat_urls in CATEGORY_URLS.items():
            for curl in cat_urls:
                cat_code = curl.split("/category/")[-1]
                if cat_code in page_url:
                    return cat_id
        return None

    async def _set_page_size_100(self, page: Page):
        """페이지당 100개 표시로 변경."""
        try:
            btn = await page.query_selector("[data-count='100'], button:has-text('100개씩')")
            if btn:
                await btn.click()
                await asyncio.sleep(3)
        except Exception:
            pass

    async def crawl(
        self, season: Optional[str] = None, max_pages: int = 10,
        dry_run: bool = False, fetch_details: bool = False
    ) -> list[dict]:
        """AJAX 페이지네이션 대응 크롤링."""
        from playwright.async_api import async_playwright
        import json

        products = []
        seen_ids = set()

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
                    category_id = self._url_to_category(url)

                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        await asyncio.sleep(5)
                        await self._set_page_size_100(page)

                        page_num = 1
                        while page_num <= 20:  # 최대 20페이지
                            cards = await page.query_selector_all(self.get_card_selector())
                            self.logger.info(f"  Page {page_num}: {len(cards)} cards")

                            for card in cards:
                                raw = await self._parse_card(card, category_id)
                                if raw and raw["id"] not in seen_ids:
                                    seen_ids.add(raw["id"])
                                    product = self.normalize_product(raw)
                                    products.append(product)
                                    if dry_run:
                                        self.logger.info(
                                            f"  [DRY] {product['product_name']} - {product['price']} KRW"
                                        )

                            # 다음 페이지 클릭
                            next_btn = await page.query_selector(".page-next:not(.disabled)")
                            if not next_btn:
                                break
                            await next_btn.click()
                            await asyncio.sleep(3)
                            page_num += 1

                        await asyncio.sleep(2)

                    except Exception as e:
                        self.logger.error(f"Page crawl failed: {url} - {e}")
                        continue

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
                            if detail.get("description"):
                                product["description"] = detail["description"]
                            if detail.get("image_urls"):
                                product["image_urls"] = json.dumps(detail["image_urls"], ensure_ascii=False)
                            self.logger.info(
                                f"  [{i+1}/{len(products)}] {product['product_name']}"
                            )
                            await asyncio.sleep(2)
                        except Exception as e:
                            self.logger.warning(f"Detail fetch failed: {e}")
                            continue
            finally:
                await browser.close()

        self.logger.info(f"Total crawled: {len(products)} products")
        return products

    async def _parse_card(self, card, category_id: Optional[str]) -> Optional[dict]:
        """상품 카드 파싱."""
        try:
            data = await card.evaluate("""(el) => {
                const link = el.querySelector('a.prod-link');
                const href = link ? link.getAttribute('href') : '';

                const nameEl = el.querySelector('.prod-title');
                const name = nameEl ? nameEl.innerText.trim() : '';

                // 할인가
                const salePriceEl = el.querySelector('.prod-price .price-group:not(.origin) .val');
                const salePrice = salePriceEl ? salePriceEl.innerText.trim().replace(/,/g, '') : '';

                // 정가
                const origPriceEl = el.querySelector('.prod-price .price-group.origin .val');
                const origPrice = origPriceEl ? origPriceEl.innerText.trim().replace(/,/g, '') : '';

                // 이미지
                const img = el.querySelector('.thumb-box-inner img');
                const imgSrc = img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : '';

                return {href, name, salePrice, origPrice, imgSrc};
            }""")

            if not data.get("name") or not data.get("href"):
                return None

            href = data["href"]
            # /DESCENTE/product/{prodCd}/{colorCd}
            match = re.search(r"/product/([^/]+)/([^/]+)", href)
            if not match:
                return None

            prod_code = match.group(1)
            color_code = match.group(2)
            # ID는 prod_code만 사용 (컬러 중복 방지)
            pid = self.make_product_id(prod_code)

            orig_price = int(data.get("origPrice") or 0)
            sale_price_val = int(data.get("salePrice") or 0)
            price = orig_price if orig_price > 0 else sale_price_val
            sale_price = sale_price_val if sale_price_val < price and sale_price_val > 0 else None

            img_url = data.get("imgSrc", "")
            if img_url.startswith("//"):
                img_url = "https:" + img_url

            product_url = f"{BASE_URL}{href}" if not href.startswith("http") else href

            return {
                "id": pid,
                "product_name": data["name"],
                "product_name_kr": data["name"],
                "price": price,
                "sale_price": sale_price,
                "currency": "KRW",
                "category_id": category_id,
                "season_id": "2026SS",
                "colors": [color_code],
                "thumbnail_url": img_url,
                "image_urls": [img_url] if img_url else [],
                "product_url": product_url,
                "style_tags": ["sportswear", "athleisure"],
            }
        except Exception as e:
            self.logger.warning(f"Descente card parse error: {e}")
            return None

    async def parse_product_card(self, page: Page, element) -> Optional[dict]:
        # crawl() 메서드에서 _parse_card로 직접 처리
        return None

    async def parse_product_detail(self, page: Page, url: str) -> dict:
        detail = {}
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)

            info = await page.evaluate("""() => {
                const result = {sizes: [], colors: [], materials: [], description: '', imageUrls: []};

                // 사이즈: prod-size-list input의 data-size-cd
                const sizeInputs = document.querySelectorAll('ul.prod-size-list input[type="radio"]');
                sizeInputs.forEach(inp => {
                    const cd = inp.getAttribute('data-size-cd') || '';
                    if (cd && !result.sizes.includes(cd)) result.sizes.push(cd);
                });

                // 컬러: rdoProdColor1 input의 value
                const colorInputs = document.querySelectorAll('.opt-color input[name="rdoProdColor1"]');
                colorInputs.forEach(inp => {
                    const code = inp.value || '';
                    if (code && !result.colors.includes(code)) result.colors.push(code);
                });

                // 소재: 상품정보제공고시 테이블에서 '소재' 행 찾기
                const specRows = document.querySelectorAll('.fold-item .fold-content table.tbl-info tr');
                specRows.forEach(row => {
                    const th = row.querySelector('th');
                    const td = row.querySelector('td');
                    if (th && td) {
                        const label = th.innerText.trim();
                        if (label.includes('소재') || label.includes('재질') || label.includes('혼용')) {
                            const matText = td.innerText.trim();
                            if (matText && matText.length > 2) {
                                // 파싱: "[BLK0]겉감1:나일론(72)폴리우레탄(28)" 형태
                                const parts = matText.split(',').map(s => s.trim()).filter(s => s.length > 2);
                                // 컬러 코드 제거하고 소재만 추출
                                parts.forEach(part => {
                                    const cleaned = part.replace(/\\[[^\\]]+\\]/g, '').trim();
                                    if (cleaned && !result.materials.includes(cleaned)) {
                                        result.materials.push(cleaned);
                                    }
                                });
                            }
                        }
                    }
                });

                // 설명: og:description
                const ogDesc = document.querySelector('meta[property="og:description"]');
                if (ogDesc) {
                    const content = ogDesc.getAttribute('content') || '';
                    if (content.length > 10) result.description = content;
                }

                // 갤러리 이미지
                const galleryImgs = document.querySelectorAll('.prod-img-wrap .swiper-slide img');
                galleryImgs.forEach(img => {
                    let src = img.getAttribute('src') || '';
                    if (src.startsWith('//')) src = 'https:' + src;
                    if (src && src.includes('dk-on.com') && !result.imageUrls.includes(src)) {
                        result.imageUrls.push(src);
                    }
                });

                return result;
            }""")

            if info.get("sizes"):
                detail["sizes"] = info["sizes"]
            if info.get("colors"):
                detail["colors"] = info["colors"]
            if info.get("materials"):
                detail["materials"] = info["materials"]
            if info.get("description"):
                detail["description"] = info["description"]
            if info.get("imageUrls"):
                detail["image_urls"] = info["imageUrls"]

        except Exception as e:
            self.logger.warning(f"Descente detail parse failed ({url}): {e}")

        return detail
