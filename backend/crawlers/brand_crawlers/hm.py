"""H&M Korea 크롤러.

대상: https://www2.hm.com/ko_kr/
카테고리 페이지에서 article[data-articlecode] 파싱.
Stealth Playwright 필요 (WAF 우회).
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www2.hm.com"

CATEGORY_URLS = {
    "outer": [
        f"{BASE_URL}/ko_kr/ladies/shop-by-product/jackets-and-coats.html",
        f"{BASE_URL}/ko_kr/men/shop-by-product/jackets-and-coats.html",
    ],
    "inner": [
        f"{BASE_URL}/ko_kr/ladies/shop-by-product/tops.html",
        f"{BASE_URL}/ko_kr/ladies/shop-by-product/knitwear.html",
        f"{BASE_URL}/ko_kr/ladies/shop-by-product/shirts-and-blouses.html",
        f"{BASE_URL}/ko_kr/men/shop-by-product/t-shirts-and-tops.html",
        f"{BASE_URL}/ko_kr/men/shop-by-product/shirts.html",
        f"{BASE_URL}/ko_kr/men/shop-by-product/hoodies-and-sweatshirts.html",
    ],
    "bottom": [
        f"{BASE_URL}/ko_kr/ladies/shop-by-product/trousers.html",
        f"{BASE_URL}/ko_kr/ladies/shop-by-product/jeans.html",
        f"{BASE_URL}/ko_kr/ladies/shop-by-product/shorts.html",
        f"{BASE_URL}/ko_kr/men/shop-by-product/trousers.html",
        f"{BASE_URL}/ko_kr/men/shop-by-product/jeans.html",
    ],
    "wear_etc": [
        f"{BASE_URL}/ko_kr/ladies/shop-by-product/dresses.html",
        f"{BASE_URL}/ko_kr/ladies/shop-by-product/skirts.html",
    ],
    "shoes": [
        f"{BASE_URL}/ko_kr/ladies/shop-by-product/shoes.html",
        f"{BASE_URL}/ko_kr/men/shop-by-product/shoes.html",
    ],
    "acc_etc": [
        f"{BASE_URL}/ko_kr/ladies/shop-by-product/accessories.html",
        f"{BASE_URL}/ko_kr/men/shop-by-product/accessories.html",
    ],
}


class HMCrawler(BaseCrawler):
    """H&M 코리아 크롤러 (stealth Playwright)."""

    def __init__(self):
        super().__init__("hm")

    async def get_product_list_urls(self, season=None):
        urls = []
        for cat_urls in CATEGORY_URLS.values():
            urls.extend(cat_urls)
        return urls

    def get_card_selector(self):
        return "article[data-articlecode]"

    def _url_to_category(self, page_url):
        for cat_id, cat_urls in CATEGORY_URLS.items():
            for curl in cat_urls:
                if curl == page_url:
                    return cat_id
        return None

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

                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        await asyncio.sleep(8)

                        # Scroll to load more (increased for full category pages)
                        for _ in range(12):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(2)
                            # Click "Load more" button if present
                            try:
                                btn = await page.query_selector('button.load-more-btn, button[data-load-more], a.load-more-heading-btn')
                                if btn:
                                    await btn.click()
                                    await asyncio.sleep(3)
                            except Exception:
                                pass

                        items = await page.evaluate("""() => {
                            const results = [];
                            const articles = document.querySelectorAll('article[data-articlecode]');
                            articles.forEach(article => {
                                const code = article.getAttribute('data-articlecode') || '';
                                const category = article.getAttribute('data-category') || '';

                                // Name & link
                                const link = article.querySelector('a[href*="productpage"]');
                                const name = link ? (link.getAttribute('title') || link.innerText.trim()) : '';
                                const href = link ? link.getAttribute('href') : '';

                                // Price
                                const priceEl = article.querySelector('[data-price], .e12bc4 span, .price');
                                const priceText = priceEl ? priceEl.innerText.trim() : '';

                                // Image
                                const img = article.querySelector('img');
                                const imgSrc = img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : '';

                                if (code && name) {
                                    results.push({code, name, href, priceText, imgSrc, category});
                                }
                            });
                            return results;
                        }""")

                        for item in items:
                            code = item.get("code", "")
                            # Use first 7 chars as style code (rest is color)
                            style_code = code[:7] if len(code) >= 7 else code
                            pid = self.make_product_id(style_code)
                            if pid in seen_ids:
                                continue
                            seen_ids.add(pid)

                            price_text = item.get("priceText", "")
                            price = int(re.sub(r"[^\d]", "", price_text.split("~")[0].split("\n")[0]) or 0)

                            img_url = item.get("imgSrc", "")
                            href = item.get("href", "")
                            product_url = href if href.startswith("http") else f"{BASE_URL}{href}"

                            raw = {
                                "id": pid,
                                "product_name": item["name"],
                                "product_name_kr": item["name"],
                                "price": price,
                                "sale_price": None,
                                "currency": "KRW",
                                "category_id": category_id,
                                "season_id": "2026SS",
                                "colors": [],
                                "thumbnail_url": img_url,
                                "image_urls": [img_url] if img_url else [],
                                "product_url": product_url,
                                "style_tags": ["spa", "fast-fashion"],
                            }
                            product = self.normalize_product(raw)
                            products.append(product)

                            if dry_run:
                                self.logger.info(f"  [DRY] {product['product_name']} - {price} KRW")

                        self.logger.info(f"Found {len(items)} items, total unique: {len(products)}")
                        await asyncio.sleep(3)

                    except Exception as e:
                        self.logger.error(f"Page crawl failed: {url} - {e}")
                        continue
            finally:
                await browser.close()

        self.logger.info(f"Total crawled: {len(products)} products")
        return products

    async def parse_product_card(self, page, element):
        return None
