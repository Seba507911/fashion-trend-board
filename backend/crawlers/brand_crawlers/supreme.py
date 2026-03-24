"""Supreme 크롤러.

대상: https://www.supremenewyork.com/shop/all
Shopify (shop.supreme.com), /shop/all 한 페이지에 전체 상품 노출.
"""
from __future__ import annotations

import asyncio
import re

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.supremenewyork.com"


class SupremeCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("supreme")

    async def get_product_list_urls(self, season=None):
        return [f"{BASE_URL}/shop/all"]

    def get_card_selector(self):
        return "a[href*='/products/']"

    async def crawl(self, season=None, max_pages=1, dry_run=False, fetch_details=False):
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth

        products, seen = [], set()
        stealth = Stealth()
        async with async_playwright() as pw:
            stealth.hook_playwright_context(pw)
            browser = await pw.chromium.launch(headless=True)
            page = await (await browser.new_context(
                viewport={"width": 1440, "height": 900}, locale="en-US",
            )).new_page()
            try:
                url = f"{BASE_URL}/shop/all"
                self.logger.info(f"Crawling: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(10)
                for _ in range(10):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(1.5)

                items = await page.evaluate("""() => {
                    const links = document.querySelectorAll('a[href*="/products/"]');
                    const seen = new Set();
                    return Array.from(links).map(a => {
                        const href = a.getAttribute('href') || '';
                        const slug = href.split('/products/')[1]?.split('?')[0]?.split('/')[0];
                        if (!slug || seen.has(slug)) return null;
                        seen.add(slug);
                        const img = a.querySelector('img');
                        const imgSrc = img ? (img.src || img.dataset.src || '') : '';
                        // Get alt text as product name fallback
                        const imgAlt = img ? (img.alt || '') : '';
                        const text = a.innerText.trim();
                        const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 1);
                        let name = '', price = '';
                        for (const l of lines) {
                            if (l.startsWith('$') || l.startsWith('¥') || l.startsWith('£')) { price = l; continue; }
                            if (l === 'sold out' || l === 'new') continue;
                            if (!name && l.length > 2) name = l;
                        }
                        // Fallback name from img alt or slug
                        if (!name) name = imgAlt || slug.replace(/[-_]/g, ' ');
                        const fullHref = href.startsWith('http') ? href : 'https://shop.supreme.com' + href;
                        return { slug, href: fullHref, name, price, img: imgSrc };
                    }).filter(x => x && x.slug);
                }""")

                for item in items:
                    pid = self.make_product_id(item["slug"][:40])
                    if pid in seen:
                        continue
                    seen.add(pid)
                    price_str = re.sub(r"[^\d]", "", item.get("price", ""))
                    raw = {
                        "id": pid, "product_name": item["name"], "product_name_kr": item["name"],
                        "price": int(price_str) if price_str else 0, "sale_price": None, "currency": "USD",
                        "category_id": None, "season_id": "2026SS", "colors": [],
                        "thumbnail_url": item["img"], "image_urls": [item["img"]] if item["img"] else [],
                        "product_url": item["href"],
                        "style_tags": ["street", "hype", "skate"],
                    }
                    products.append(self.normalize_product(raw))

                self.logger.info(f"Found {len(items)} items, total unique: {len(products)}")

            except Exception as e:
                self.logger.error(f"Failed: {url} - {e}")
            finally:
                await browser.close()

        self.logger.info(f"Total: {len(products)}")
        return products

    async def parse_product_card(self, page, element):
        return None
