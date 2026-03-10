"""The North Face Korea 공식몰 크롤러.

대상: https://www.thenorthfacekorea.co.kr/
카테고리: /category/n/{gender}/{category}/{subcategory}
상품 카드: 서버 렌더링 HTML + 무한 스크롤 (Playwright 필요)
상세 URL: /product/{PRODUCT_CODE}
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
        return "a[href^='/product/']"

    def _url_to_category(self, page_url: str) -> Optional[str]:
        for cat_id, cat_urls in CATEGORY_URLS.items():
            for curl in cat_urls:
                path = curl.replace(BASE_URL, "")
                if path in page_url:
                    return cat_id
        return None

    async def _scroll_to_load_all(self, page: Page, max_scrolls: int = 15):
        """무한 스크롤로 모든 상품 로드."""
        prev_count = 0
        for _ in range(max_scrolls):
            count = await page.evaluate(
                "document.querySelectorAll(\"a[href^='/product/']\").length"
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
                            const links = document.querySelectorAll("a[href^='/product/']");
                            links.forEach(a => {
                                const href = a.getAttribute('href') || '';
                                const codeMatch = href.match(/\\/product\\/([A-Z0-9]+)/);
                                if (!codeMatch) return;

                                const card = a.closest('[class*="product"]') || a.parentElement;
                                if (!card) return;

                                const img = card.querySelector('img');
                                const imgSrc = img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : '';

                                const text = card.innerText || '';
                                const lines = text.split('\\n').map(l => l.trim()).filter(l => l);

                                // 가격 추출
                                const priceMatches = text.match(/([\\d,]+)원/g) || [];
                                let price = 0;
                                let salePrice = null;
                                if (priceMatches.length >= 2) {
                                    price = parseInt(priceMatches[0].replace(/[^\\d]/g, '')) || 0;
                                    salePrice = parseInt(priceMatches[1].replace(/[^\\d]/g, '')) || 0;
                                } else if (priceMatches.length === 1) {
                                    price = parseInt(priceMatches[0].replace(/[^\\d]/g, '')) || 0;
                                }

                                // 상품명: 가격이 아닌 첫 번째 텍스트 라인
                                let name = '';
                                for (const line of lines) {
                                    if (!line.match(/[\\d,]+원/) && !line.match(/^\\d+%$/) && line.length > 2) {
                                        name = line;
                                        break;
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
                            pid = self.make_product_id(code)
                            if pid in seen_ids or not item.get("name"):
                                continue
                            seen_ids.add(pid)

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
                                "thumbnail_url": item.get("imgSrc", ""),
                                "image_urls": [item["imgSrc"]] if item.get("imgSrc") else [],
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

            info = await page.evaluate("""() => {
                const result = {sizes: [], colors: [], materials: [], description: ''};

                // 사이즈
                const sizeEls = document.querySelectorAll('[class*="size"] button, [class*="size"] a, [class*="size"] span');
                sizeEls.forEach(el => {
                    const text = el.innerText.trim();
                    if (text && text.match(/^\\d{2,3}/) && !text.includes('가이드')) {
                        result.sizes.push(text);
                    }
                });

                // 컬러 (다른 컬러 링크)
                const colorLinks = document.querySelectorAll('a[href*="/product/"]');
                colorLinks.forEach(a => {
                    const title = a.getAttribute('title') || a.getAttribute('aria-label') || '';
                    if (title && title !== '' && !result.colors.includes(title)) {
                        result.colors.push(title);
                    }
                });

                // 소재
                const allText = document.body.innerText || '';
                const matMatches = allText.match(/[가-힣A-Za-z]+\\s*\\d+%/g) || [];
                const matMatches2 = allText.match(/\\d+%\\s*[가-힣A-Za-z]+/g) || [];
                const mats = [...new Set([...matMatches, ...matMatches2])];
                result.materials = mats.filter(m => !m.includes('할인') && !m.includes('적립')).slice(0, 5);

                // 설명
                const descEl = document.querySelector('[class*="detail"], [class*="description"], [class*="info"]');
                if (descEl) result.description = descEl.innerText.trim().substring(0, 500);

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

        except Exception as e:
            self.logger.warning(f"NF detail parse failed ({url}): {e}")

        return detail
