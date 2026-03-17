"""The North Face Korea 공식몰 크롤러.

대상: https://www.thenorthfacekorea.co.kr/
카테고리: /category/n/{gender}/{category}/{subcategory}
상품 카드: 서버 렌더링 HTML + 무한 스크롤 (Playwright 필요)
상세 URL: /product/{PRODUCT_CODE}
코드 구조: 7자리 base + 1자리 color suffix (예: NJ2HS06 + D)
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from playwright.async_api import Page

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.thenorthfacekorea.co.kr"

CATEGORY_URLS = {
    "outer": [
        f"{BASE_URL}/category/n/men/jacket-vest",
        f"{BASE_URL}/category/n/women/jacket-vest",
    ],
    "top": [
        f"{BASE_URL}/category/n/men/top",
        f"{BASE_URL}/category/n/women/top",
    ],
    "bottom": [
        f"{BASE_URL}/category/n/men/bottom",
        f"{BASE_URL}/category/n/women/bottom",
    ],
    "down": [
        f"{BASE_URL}/category/n/men/down",
        f"{BASE_URL}/category/n/women/down",
    ],
    "shoes": [
        f"{BASE_URL}/category/n/men/shoes",
        f"{BASE_URL}/category/n/women/shoes",
    ],
    "bag": [
        f"{BASE_URL}/category/n/men/bag-acc/bag",
    ],
    "accessories": [
        f"{BASE_URL}/category/n/men/bag-acc/accessories",
    ],
}


class NorthFaceCrawler(BaseCrawler):
    """노스페이스 코리아 크롤러."""

    def __init__(self):
        super().__init__("northface")

    async def get_product_list_urls(self, season: Optional[str] = None) -> list[str]:
        urls = []
        for cat_urls in CATEGORY_URLS.values():
            urls.extend(cat_urls)
        return urls

    def get_card_selector(self) -> str:
        return "li.plp-grid-item"

    def _url_to_category(self, page_url: str) -> Optional[str]:
        for cat_id, cat_urls in CATEGORY_URLS.items():
            for curl in cat_urls:
                path = curl.replace(BASE_URL, "")
                if path in page_url:
                    return cat_id
        return None

    @staticmethod
    def _base_code(code: str) -> str:
        """상품코드에서 컬러 접미사(마지막 1자) 제거 → 스타일 기본코드."""
        if len(code) >= 8 and code[-1].isalpha():
            return code[:-1]
        return code

    async def _scroll_to_load_all(self, page: Page, max_scrolls: int = 15):
        """무한 스크롤로 모든 상품 로드."""
        prev_count = 0
        for _ in range(max_scrolls):
            count = await page.evaluate(
                "document.querySelectorAll(\"li.plp-grid-item\").length"
            )
            if count == prev_count:
                break
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
                        await self._scroll_to_load_all(page)

                        items = await page.evaluate("""() => {
                            const results = [];
                            const cards = document.querySelectorAll('li.plp-grid-item');
                            cards.forEach(card => {
                                // 이미지
                                const img = card.querySelector('img');
                                const imgSrc = img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : '';

                                // 상품명
                                const nameEl = card.querySelector('p.name a');
                                const name = nameEl ? nameEl.innerText.trim() : '';

                                // 상품 링크
                                const linkEl = card.querySelector("a[href^='/product/']");
                                const href = linkEl ? linkEl.getAttribute('href') : '';
                                const codeMatch = href.match(/\\/product\\/([A-Z0-9]+)/);
                                if (!codeMatch || !name) return;

                                // 가격: "269,000 원" 또는 "269,000" 형태
                                const text = card.innerText || '';
                                const priceMatches = text.match(/([\\d,]+)\\s*원/g) || [];
                                let price = 0;
                                let salePrice = null;
                                if (priceMatches.length >= 2) {
                                    price = parseInt(priceMatches[0].replace(/[^\\d]/g, '')) || 0;
                                    salePrice = parseInt(priceMatches[1].replace(/[^\\d]/g, '')) || 0;
                                } else if (priceMatches.length === 1) {
                                    price = parseInt(priceMatches[0].replace(/[^\\d]/g, '')) || 0;
                                }
                                // fallback: data-price 속성
                                if (price === 0) {
                                    const priceEl = card.querySelector('[data-price]');
                                    if (priceEl) price = parseInt(priceEl.getAttribute('data-price')) || 0;
                                }
                                // fallback: span.price strong
                                if (price === 0) {
                                    const priceStrong = card.querySelector('.price strong, span.price');
                                    if (priceStrong) {
                                        const pText = priceStrong.innerText.replace(/[^\\d]/g, '');
                                        price = parseInt(pText) || 0;
                                    }
                                }

                                results.push({
                                    code: codeMatch[1],
                                    name: name,
                                    imgSrc: imgSrc,
                                    price: price,
                                    salePrice: salePrice && salePrice < price ? salePrice : null,
                                    href: href,
                                });
                            });
                            return results;
                        }""")

                        for item in items:
                            code = item.get("code", "")
                            # 컬러 접미사 제거한 base code로 ID 생성
                            base = self._base_code(code)
                            pid = self.make_product_id(base)
                            if pid in seen_ids or not item.get("name"):
                                continue
                            seen_ids.add(pid)

                            img_url = item.get("imgSrc", "")
                            if img_url and not img_url.startswith("http"):
                                img_url = "https:" + img_url if img_url.startswith("//") else f"https://www.thenorthfacekorea.co.kr{img_url}"

                            raw = {
                                "id": pid,
                                "product_name": item["name"],
                                "product_name_kr": item["name"],
                                "price": item.get("price", 0),
                                "sale_price": item.get("salePrice"),
                                "currency": "KRW",
                                "category_id": category_id,
                                "season_id": "2026SS",
                                "colors": [],
                                "thumbnail_url": img_url,
                                "image_urls": [img_url] if img_url else [],
                                "product_url": f"{BASE_URL}{item['href']}" if not item["href"].startswith("http") else item["href"],
                                "style_tags": ["outdoor", "sportswear"],
                            }
                            product = self.normalize_product(raw)
                            products.append(product)

                            if dry_run:
                                self.logger.info(f"  [DRY] {product['product_name']} - {product['price']} KRW")

                        self.logger.info(f"Found {len(items)} items, total unique: {len(products)}")
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

    async def parse_product_card(self, page: Page, element) -> Optional[dict]:
        # crawl() 메서드에서 직접 JS evaluate로 처리
        return None

    async def parse_product_detail(self, page: Page, url: str) -> dict:
        detail = {}
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)

            # "상세보기" / 접힌 상세 영역 펼치기
            try:
                fold_btns = await page.query_selector_all(
                    "button.pdp-details-toggle, "
                    "button[aria-label*='상세'], "
                    ".pdp-details button, "
                    ".product-details-toggle, "
                    "button:has-text('상세'), "
                    "button:has-text('더보기'), "
                    "a.btn-more-view"
                )
                for btn in fold_btns:
                    try:
                        await btn.click()
                        await asyncio.sleep(1)
                    except Exception:
                        pass
                await asyncio.sleep(1)
            except Exception:
                pass

            info = await page.evaluate("""() => {
                const result = {sizes: [], colors: [], materials: [], description: '', imageUrls: []};

                // 사이즈: label.variation-size > span.variation-anchor
                const sizeLabels = document.querySelectorAll('label.variation-size span.variation-anchor');
                sizeLabels.forEach(el => {
                    const text = el.innerText.trim();
                    if (text && !result.sizes.includes(text)) {
                        result.sizes.push(text);
                    }
                });

                // 컬러: span.value 에서 현재 컬러명
                const colorVal = document.querySelector('.product-information span.label + span.value');
                if (colorVal) {
                    const colorText = colorVal.innerText.trim();
                    if (colorText && colorText !== '') {
                        result.colors.push(colorText);
                    }
                }
                // 다른 컬러 변형 링크
                const swatchLinks = document.querySelectorAll('.swatch-list-color a[href*="/product/"]');
                swatchLinks.forEach(a => {
                    const title = a.getAttribute('title') || '';
                    if (title && !result.colors.includes(title)) {
                        result.colors.push(title);
                    }
                });

                // 소재: dt.tag-key "제품 소재" → dd.tag-value
                const dtEls = document.querySelectorAll('dt.tag-key, dt, th');
                dtEls.forEach(dt => {
                    const label = dt.innerText.trim();
                    if (label.includes('소재') || label.includes('재질') || label.includes('혼용')) {
                        const dd = dt.nextElementSibling;
                        if (dd) {
                            const matText = dd.innerText.trim();
                            if (matText && matText.length > 2) {
                                result.materials.push(matText);
                            }
                        }
                    }
                });
                // 소재 fallback: 상세 영역에서 % 패턴 추출
                if (result.materials.length === 0) {
                    const allText = document.body.innerText || '';
                    const matPatterns = allText.match(/(?:겉감|안감|충전재|주머니감|배색)\s*[:\s]*[가-힣A-Za-z]+\s*\d+%[^\\n]*/g);
                    if (matPatterns) {
                        matPatterns.forEach(m => {
                            if (!result.materials.includes(m.trim())) result.materials.push(m.trim());
                        });
                    }
                }

                // 설명: 여러 후보 셀렉터
                const descSels = [
                    '.pdp-details-content', '.product-description',
                    '.pdp-body', '.product-detail-info', '.detail-info'
                ];
                for (const sel of descSels) {
                    const el = document.querySelector(sel);
                    if (el) {
                        const text = el.innerText.trim();
                        if (text.length > 10) {
                            result.description = text.substring(0, 500);
                            break;
                        }
                    }
                }
                // 설명 fallback: og:description
                if (!result.description) {
                    const ogDesc = document.querySelector('meta[property="og:description"]');
                    if (ogDesc) {
                        const content = ogDesc.getAttribute('content') || '';
                        if (content.length > 10) result.description = content;
                    }
                }

                // 갤러리 이미지
                const galleryImgs = document.querySelectorAll('.product-gallery-slide img, .slide.product-gallery-slide img');
                galleryImgs.forEach(img => {
                    const src = img.getAttribute('src') || '';
                    if (src && src.includes('thenorthface') && !result.imageUrls.includes(src)) {
                        result.imageUrls.push(src);
                    }
                });

                return result;
            }""")

            if info.get("sizes"):
                # 중복 제거
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
            self.logger.warning(f"NF detail parse failed ({url}): {e}")

        return detail
