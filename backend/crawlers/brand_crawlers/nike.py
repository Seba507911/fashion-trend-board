"""Nike Korea 공식몰 크롤러.

대상: https://www.nike.com/kr
카테고리: /kr/w/{gender}-{category}-{filter_codes}
상품 카드: .product-card (Next.js SSR 렌더링)
상세 URL: /kr/t/{product-slug}/{STYLECODE}-{COLORCODE}
코드 구조: 스타일코드 + 하이픈 + 컬러코드 (예: IF1144-551)
무한 스크롤 기반 페이지네이션
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from playwright.async_api import Page

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.nike.com"

# 남성/여성 × 카테고리별 URL
CATEGORY_URLS: dict[str, list[str]] = {
    "outer": [
        f"{BASE_URL}/kr/w/mens-jackets-vests-50r7yznik1",
        f"{BASE_URL}/kr/w/womens-jackets-vests-50r7yz5e1x6",
    ],
    "inner": [
        f"{BASE_URL}/kr/w/mens-tops-t-shirts-9om13znik1",
        f"{BASE_URL}/kr/w/womens-tops-t-shirts-5e1x6z9om13",
    ],
    "bottom": [
        f"{BASE_URL}/kr/w/mens-pants-tights-2kq19znik1",
        f"{BASE_URL}/kr/w/womens-pants-tights-2kq19z5e1x6",
    ],
    "shoes": [
        f"{BASE_URL}/kr/w/mens-shoes-nik1zy7ok",
        f"{BASE_URL}/kr/w/womens-shoes-5e1x6zy7ok",
    ],
}


class NikeCrawler(BaseCrawler):
    """나이키 코리아 크롤러."""

    def __init__(self):
        super().__init__("nike")

    async def get_product_list_urls(self, season: Optional[str] = None) -> list[str]:
        urls = []
        for cat_urls in CATEGORY_URLS.values():
            urls.extend(cat_urls)
        return urls

    def get_card_selector(self) -> str:
        return ".product-card"

    def _url_to_category(self, page_url: str) -> Optional[str]:
        """URL 경로로 카테고리 매핑."""
        for cat_id, cat_urls in CATEGORY_URLS.items():
            for curl in cat_urls:
                # URL의 경로 부분만 비교
                path = curl.replace(BASE_URL, "")
                if path in page_url:
                    return cat_id
        return None

    @staticmethod
    def _extract_style_code(url: str) -> tuple[str, str]:
        """URL에서 스타일코드와 컬러코드 분리.

        /kr/t/product-name/IF1144-551 → ("IF1144", "551")
        """
        match = re.search(r"/([A-Z0-9]{5,10})-(\d{3})(?:\?|$|#)", url)
        if match:
            return match.group(1), match.group(2)
        # 컬러코드 없는 경우
        match2 = re.search(r"/([A-Z0-9]{5,10})(?:\?|$|#)", url)
        if match2:
            return match2.group(1), ""
        return "", ""

    @staticmethod
    def _parse_price(price_text: str) -> int:
        """가격 텍스트에서 숫자 추출. '219,000 원' → 219000"""
        digits = re.sub(r"[^\d]", "", price_text)
        return int(digits) if digits else 0

    async def _scroll_to_load_all(self, page: Page, max_scrolls: int = 20):
        """무한 스크롤로 모든 상품 로드."""
        prev_count = 0
        no_change_count = 0
        for _ in range(max_scrolls):
            count = await page.evaluate(
                'document.querySelectorAll(".product-card").length'
            )
            if count == prev_count:
                no_change_count += 1
                if no_change_count >= 2:
                    break
            else:
                no_change_count = 0
            prev_count = count
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

    async def crawl(
        self, season: Optional[str] = None, max_pages: int = 10,
        dry_run: bool = False, fetch_details: bool = False
    ) -> list[dict]:
        """무한 스크롤 대응 크롤링."""
        from playwright.async_api import async_playwright
        import json

        products: list[dict] = []
        seen_ids: set[str] = set()

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
                        await self._scroll_to_load_all(page)

                        items = await page.evaluate("""() => {
                            const results = [];
                            const cards = document.querySelectorAll('.product-card');
                            cards.forEach(card => {
                                // 상품 링크 (스타일코드 포함)
                                const link = card.querySelector('a[href*="/t/"]');
                                const href = link ? link.getAttribute('href') : '';
                                if (!href) return;

                                // 상품명
                                const titleEl = card.querySelector('.product-card__title');
                                const title = titleEl ? titleEl.innerText.trim() : '';
                                if (!title) return;

                                // 서브타이틀 (카테고리/컬러 정보)
                                const subtitleEl = card.querySelector('.product-card__subtitle');
                                const subtitle = subtitleEl ? subtitleEl.innerText.trim() : '';

                                // 가격: 정가와 할인가
                                const priceEl = card.querySelector('.product-price');
                                let priceText = '';
                                let salePriceText = '';
                                if (priceEl) {
                                    // 할인 시: "139,000 원 99,000 원" 또는 여러 span
                                    const fullPriceEl = priceEl.querySelector('.product-price__original, del, s');
                                    const currentPriceEl = priceEl.querySelector('.product-price__discounted, .product-price__reduced');
                                    if (fullPriceEl && currentPriceEl) {
                                        priceText = fullPriceEl.innerText.trim();
                                        salePriceText = currentPriceEl.innerText.trim();
                                    } else {
                                        priceText = priceEl.innerText.trim();
                                    }
                                }

                                // 이미지
                                const img = card.querySelector('img');
                                const imgSrc = img ? (img.getAttribute('src') || '') : '';

                                results.push({
                                    href: href,
                                    title: title,
                                    subtitle: subtitle,
                                    priceText: priceText,
                                    salePriceText: salePriceText,
                                    imgSrc: imgSrc,
                                });
                            });
                            return results;
                        }""")

                        for item in items:
                            href = item.get("href", "")
                            style_code, color_code = self._extract_style_code(href)
                            if not style_code or not item.get("title"):
                                continue

                            # 스타일코드만으로 ID 생성 (컬러별 중복 제거)
                            pid = self.make_product_id(style_code)
                            if pid in seen_ids:
                                continue
                            seen_ids.add(pid)

                            price = self._parse_price(item.get("priceText", ""))
                            sale_price_val = self._parse_price(item.get("salePriceText", ""))
                            sale_price = sale_price_val if sale_price_val and sale_price_val < price else None

                            img_url = item.get("imgSrc", "")

                            # subtitle에서 컬러 힌트 추출 (예: "남성 스톰 핏 ADV 재킷")
                            # Nike subtitle은 보통 성별+카테고리 설명이므로 color는 별도 추출
                            colors = [color_code] if color_code else []

                            # 전체 URL 구성
                            product_url = href
                            if not product_url.startswith("http"):
                                product_url = f"{BASE_URL}{product_url}"

                            raw = {
                                "id": pid,
                                "product_name": item["title"],
                                "product_name_kr": item["title"],
                                "price": price,
                                "sale_price": sale_price,
                                "currency": "KRW",
                                "category_id": category_id,
                                "season_id": "2026SS",
                                "colors": colors,
                                "thumbnail_url": img_url,
                                "image_urls": [img_url] if img_url else [],
                                "product_url": product_url,
                                "style_tags": ["sportswear", "lifestyle"],
                            }
                            product = self.normalize_product(raw)
                            products.append(product)

                            if dry_run:
                                self.logger.info(
                                    f"  [DRY] {product['product_name']} - "
                                    f"{product['price']} KRW ({style_code})"
                                )

                        self.logger.info(
                            f"Found {len(items)} items, total unique: {len(products)}"
                        )
                        # 카테고리간 크롤 딜레이
                        await asyncio.sleep(3)

                    except Exception as e:
                        self.logger.error(f"Page crawl failed: {url} - {e}")
                        continue

                # 상세 페이지 크롤링 (옵션)
                if fetch_details and not dry_run:
                    self.logger.info(f"Fetching details for {len(products)} products...")
                    for idx, product in enumerate(products):
                        purl = product.get("product_url")
                        if not purl:
                            continue
                        try:
                            detail = await self.parse_product_detail(page, purl)
                            if detail.get("colors"):
                                product["colors"] = json.dumps(
                                    detail["colors"], ensure_ascii=False
                                )
                            if detail.get("sizes"):
                                product["sizes"] = json.dumps(
                                    detail["sizes"], ensure_ascii=False
                                )
                            if detail.get("materials"):
                                product["materials"] = json.dumps(
                                    detail["materials"], ensure_ascii=False
                                )
                            if detail.get("description"):
                                product["description"] = detail["description"]
                            if detail.get("image_urls"):
                                product["image_urls"] = json.dumps(
                                    detail["image_urls"], ensure_ascii=False
                                )
                            self.logger.info(
                                f"  [{idx+1}/{len(products)}] {product['product_name']}"
                            )
                            await asyncio.sleep(3)
                        except Exception as e:
                            self.logger.warning(f"Detail fetch failed: {e}")
                            continue
            finally:
                await browser.close()

        self.logger.info(f"Total crawled: {len(products)} products")
        return products

    async def parse_product_card(self, page: Page, element) -> Optional[dict]:
        # crawl() 메서드에서 직접 JS evaluate로 처리
        return None

    async def parse_product_detail(self, page: Page, url: str) -> dict:
        """상품 상세 페이지에서 추가 정보 추출."""
        detail: dict = {}
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)

            # 소재/상세 탭 클릭 시도
            try:
                tab_btns = await page.query_selector_all(
                    "button:has-text('상품 정보'), "
                    "button:has-text('제품 상세'), "
                    "button:has-text('소재'), "
                    "[role='tab']:has-text('정보'), "
                    "[role='tab']:has-text('상세')"
                )
                for btn in tab_btns:
                    try:
                        await btn.click()
                        await asyncio.sleep(1)
                    except Exception:
                        pass
            except Exception:
                pass

            info = await page.evaluate("""() => {
                const result = {sizes: [], colors: [], materials: [], description: '', imageUrls: []};

                // 사이즈: 사이즈 선택 버튼들
                const sizeButtons = document.querySelectorAll(
                    '[data-testid="size-selector"] label, ' +
                    '.size-selector-list button, ' +
                    '[aria-label*="사이즈"] button'
                );
                sizeButtons.forEach(btn => {
                    const text = btn.innerText.trim();
                    if (text && !result.sizes.includes(text)) {
                        result.sizes.push(text);
                    }
                });

                // 컬러: 컬러 셀렉터 영역
                const colorLabel = document.querySelector(
                    '[data-testid="color-description"], ' +
                    '.colorway-title, ' +
                    '.description-preview__color-description'
                );
                if (colorLabel) {
                    const colorText = colorLabel.innerText.trim();
                    if (colorText) {
                        result.colors.push(colorText);
                    }
                }
                // 다른 컬러 변형 링크
                const colorSwatches = document.querySelectorAll(
                    '[data-testid="colorway-link"], ' +
                    '.colorway-images a[href*="/t/"]'
                );
                colorSwatches.forEach(a => {
                    const title = a.getAttribute('aria-label') || a.getAttribute('title') || '';
                    if (title && !result.colors.includes(title)) {
                        result.colors.push(title);
                    }
                });

                // 소재: 페이지 텍스트에서 추출
                const allPageText = document.body.innerText || '';
                // "소재:" / "Material:" 패턴 — RegExp 생성자 사용 (슬래시 이스케이프 회피)
                const matRe = new RegExp('(?:소재|Material|원단)[:\\s]+([\\s\\S]{5,200}?)(?:\\n\\n|제조|세탁|원산지|A.S)', 'i');
                const matMatch = allPageText.match(matRe);
                if (matMatch) {
                    const lines = matMatch[1].split('\\n').map(s => s.trim()).filter(s => s.length > 2);
                    lines.forEach(l => {
                        if (!result.materials.includes(l)) result.materials.push(l);
                    });
                }
                // fallback: 퍼센트 패턴 추출
                if (result.materials.length === 0) {
                    const pctRe = new RegExp('[가-힣A-Za-z]+\\s*\\d+%', 'g');
                    const pctMatches = allPageText.match(pctRe);
                    if (pctMatches) {
                        pctMatches.slice(0, 5).forEach(m => {
                            if (!m.includes('할인') && !m.includes('쿠폰') && !result.materials.includes(m)) {
                                result.materials.push(m);
                            }
                        });
                    }
                }

                // 설명
                const descEl = document.querySelector(
                    '.description-preview__body, ' +
                    '[data-testid="product-description"], ' +
                    '.product-info__description'
                );
                if (descEl) {
                    const text = descEl.innerText.trim();
                    if (text.length > 10) result.description = text.substring(0, 500);
                }

                // 갤러리 이미지
                const galleryImgs = document.querySelectorAll(
                    '.hero-image img, ' +
                    '[data-testid="HeroImg"] img, ' +
                    '.css-1m0gqys img'
                );
                const seenUrls = new Set();
                galleryImgs.forEach(img => {
                    const src = img.getAttribute('src') || '';
                    if (src && src.includes('static.nike.com') && !seenUrls.has(src)) {
                        seenUrls.add(src);
                        result.imageUrls.push(src);
                    }
                });

                return result;
            }""")

            if info.get("sizes"):
                detail["sizes"] = list(dict.fromkeys(info["sizes"]))
            if info.get("colors"):
                detail["colors"] = info["colors"]
            if info.get("materials"):
                detail["materials"] = info["materials"]
            if info.get("description"):
                detail["description"] = info["description"]
            if info.get("imageUrls"):
                detail["image_urls"] = info["imageUrls"]

        except Exception as e:
            self.logger.warning(f"Nike detail parse failed ({url}): {e}")

        return detail
