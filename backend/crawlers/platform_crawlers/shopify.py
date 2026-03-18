"""Shopify 플랫폼 크롤러.

Shopify 기반 쇼핑몰의 공통 크롤링 로직.
브랜드별로 config만 전달하면 동작한다.

Config 형태:
    {
        "brand_id": "alo",
        "base_url": "https://www.aloyoga.com",
        "collections": {
            "tops": "top",             # slug → category_id
            "womens-jackets": "outer",
        },
        "card_selector": ".PlpTile",   # 선택 (기본: .product-card)
        "selectors": {                 # 선택 (기본값 있음)
            "name": ".product-name p",
            "price": ".product-price",
            "color": ".product-color",
            "image": ".product-carousel img",
            "link": "a[href*='/products/']",
        },
        "style_tags": ["athleisure", "yoga"],
        "currency": "USD",
        "season_id": "2026SS",
    }
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from playwright.async_api import Page

from backend.crawlers.base_crawler import BaseCrawler

# 기본 셀렉터
DEFAULT_SELECTORS = {
    "name": ".product-name p, .product-card__title, .product-title, h3 a",
    "price": ".product-price, .price, .product-card__price",
    "color": ".product-color, .color-name, .product-card__color",
    "image": ".product-carousel img, .product-card__image img, .product-image img",
    "link": "a[href*='/products/']",
}

DEFAULT_DETAIL_SELECTORS = {
    "sizes": ".button-size-selector__button, .size-selector button, .size-option",
    "color_swatches": ".swatches .swatch__wrapper a, .core-swatches a, .swatch-label",
    "description": ".description, .product-description, .product__description",
    "fabrication": ".fabrication, .product-fabrication",
    "fit": "[class*='quickFitText'], [class*='fit-text'], .fit-info",
}


class ShopifyCrawler(BaseCrawler):
    """Shopify 플랫폼 공통 크롤러."""

    def __init__(self, config: dict):
        super().__init__(config["brand_id"])
        self.config = config
        self.base_url = config["base_url"].rstrip("/")
        self.collections = config.get("collections", {})
        self.style_tags = config.get("style_tags", [])
        self.season_id = config.get("season_id", "2026SS")
        self.currency = config.get("currency", "USD")
        self._card_selector = config.get("card_selector", ".product-card")
        self._selectors = {**DEFAULT_SELECTORS, **config.get("selectors", {})}
        self._detail_selectors = {**DEFAULT_DETAIL_SELECTORS, **config.get("detail_selectors", {})}

    async def get_product_list_urls(self, season: Optional[str] = None) -> list[str]:
        return [
            f"{self.base_url}/collections/{slug}"
            for slug in self.collections.keys()
        ]

    def get_card_selector(self) -> str:
        return self._card_selector

    def _url_to_category(self, page_url: str) -> Optional[str]:
        for slug, cat_id in self.collections.items():
            if f"/collections/{slug}" in page_url:
                return cat_id
        return None

    async def parse_product_card(self, page: Page, element) -> Optional[dict]:
        try:
            s = self._selectors
            name_el = await element.query_selector(s["name"]) if s.get("name") else None
            price_el = await element.query_selector(s["price"]) if s.get("price") else None
            color_el = await element.query_selector(s["color"]) if s.get("color") else None
            img_el = await element.query_selector(s["image"]) if s.get("image") else None
            link_el = await element.query_selector(s["link"]) if s.get("link") else None

            name = await name_el.inner_text() if name_el else None
            if not name:
                return None
            name = name.strip()

            price_text = await price_el.inner_text() if price_el else "0"
            price_raw = price_text.split("\n")[0].strip()
            # 유럽식 "2.900€" 또는 "2.900,00€" → 2900
            # 미국식 "$129.00" → 129.00
            if re.search(r"\d\.\d{3}(?:[,€]|$)", price_raw):
                # 유럽식: . = 천단위, , = 소수점
                price_num = re.sub(r"[^\d,]", "", price_raw).replace(",", ".")
            else:
                price_num = re.sub(r"[^\d.]", "", price_raw)
            price = float(price_num) if price_num else 0

            color = ""
            if color_el:
                color = (await color_el.inner_text()).strip()

            img_url = None
            if img_el:
                img_url = await img_el.get_attribute("src")
                if not img_url:
                    img_url = await img_el.get_attribute("data-src")
                if not img_url:
                    img_url = await img_el.get_attribute("srcset")
                    if img_url:
                        img_url = img_url.split(",")[0].strip().split(" ")[0]
            # Also try <source> inside <picture>
            if not img_url:
                source_el = await element.query_selector("picture source[srcset]")
                if source_el:
                    srcset = await source_el.get_attribute("srcset")
                    if srcset:
                        img_url = srcset.split(",")[-1].strip().split(" ")[0]
            if img_url and img_url.startswith("//"):
                img_url = "https:" + img_url
            if img_url and "_320x" in img_url:
                img_url = img_url.replace("_320x", "_600x")

            link = await link_el.get_attribute("href") if link_el else None
            product_url = link if link and link.startswith("http") else f"{self.base_url}{link}" if link else None

            code = ""
            if link:
                match = re.search(r"/products/([^/?]+)", link)
                code = match.group(1) if match else re.sub(r"[^a-zA-Z0-9]", "", name)[:30]

            category_id = self._url_to_category(page.url)

            return {
                "id": self.make_product_id(code),
                "product_name": name,
                "product_name_kr": name,
                "price": price,
                "currency": self.currency,
                "category_id": category_id,
                "season_id": self.season_id,
                "colors": [color] if color else [],
                "thumbnail_url": img_url,
                "image_urls": [img_url] if img_url else [],
                "product_url": product_url,
                "style_tags": self.style_tags,
            }
        except Exception as e:
            self.logger.warning(f"Shopify card parse error: {e}")
            return None

    async def parse_product_detail(self, page: Page, url: str) -> dict:
        detail = {}
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)

            ds = self._detail_selectors

            # 사이즈
            size_els = await page.query_selector_all(ds["sizes"])
            sizes = []
            for el in size_els:
                text = (await el.inner_text()).strip()
                if text:
                    sizes.append(text)
            if sizes:
                detail["sizes"] = sizes

            # 컬러 스워치
            colors = await page.evaluate("""(selector) => {
                const colors = [];
                const swatches = document.querySelectorAll(selector);
                swatches.forEach(a => {
                    const title = a.getAttribute('title') || a.getAttribute('aria-label') || a.innerText.trim();
                    const clean = title.replace(/^Color:\\s*/i, '');
                    if (clean && !colors.includes(clean)) colors.push(clean);
                });
                if (colors.length === 0) {
                    const colorEl = document.querySelector('.product-color, .selected-option');
                    if (colorEl) {
                        let text = colorEl.innerText.trim().replace(/^Color:\\s*/i, '');
                        if (text) colors.push(text);
                    }
                }
                return colors;
            }""", ds["color_swatches"])
            if colors:
                detail["colors"] = colors

            # 설명 + 핏
            desc_el = await page.query_selector(ds["description"])
            if desc_el:
                full_text = (await desc_el.inner_text()).strip()
                sections = re.split(r"\n(?=DESCRIPTION|FIT|FABRICATION)", full_text)
                for section in sections:
                    s = section.strip()
                    if s.startswith("DESCRIPTION"):
                        detail["description"] = s.replace("DESCRIPTION", "", 1).strip()
                    elif s.startswith("FIT"):
                        detail["fit_info"] = s.replace("FIT", "", 1).strip()
                if "description" not in detail and full_text:
                    detail["description"] = full_text[:500]

            # 소재
            fab_el = await page.query_selector(ds["fabrication"])
            if fab_el:
                fab_text = (await fab_el.inner_text()).strip()
                materials = re.findall(r"\d+%\s*[A-Za-z]+", fab_text)
                if materials:
                    detail["materials"] = materials

            # 핏 (별도 요소)
            if "fit_info" not in detail:
                fit_el = await page.query_selector(ds["fit"])
                if fit_el:
                    detail["fit_info"] = (await fit_el.inner_text()).strip()

        except Exception as e:
            self.logger.warning(f"Shopify detail parse failed ({url}): {e}")

        return detail
