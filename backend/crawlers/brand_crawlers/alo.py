"""ALO Yoga 글로벌 공식몰 크롤러.

대상: https://www.aloyoga.com/
Shopify 기반, 카테고리: /collections/{slug}
상세 페이지에서 사이즈/컬러/소재/핏/설명 수집
"""
import asyncio
import re
from typing import Optional

from playwright.async_api import Page

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.aloyoga.com"

CATEGORY_MAP = {
    "tops": "top",
    "womens-jackets": "outer",
    "womens-leggings": "bottom",
    "pants": "bottom",
    "womens-shorts": "bottom",
    "womens-sweatshirts-hoodies": "top",
    "bras": "top",
    "shoes": "sneakers",
    "dresses": "dress",
    "accessories-shop-all": "etc_acc",
}


class AloCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("alo")

    async def get_product_list_urls(self, season: Optional[str] = None) -> list[str]:
        return [
            f"{BASE_URL}/collections/tops",
            f"{BASE_URL}/collections/womens-jackets",
            f"{BASE_URL}/collections/womens-leggings",
            f"{BASE_URL}/collections/pants",
            f"{BASE_URL}/collections/shoes",
            f"{BASE_URL}/collections/womens-sweatshirts-hoodies",
        ]

    def get_card_selector(self) -> str:
        return ".PlpTile"

    def _url_to_category(self, page_url: str) -> Optional[str]:
        """현재 페이지 URL에서 카테고리 ID 추출."""
        for slug, cat_id in CATEGORY_MAP.items():
            if slug in page_url:
                return cat_id
        return None

    async def parse_product_card(self, page: Page, element) -> Optional[dict]:
        try:
            name_el = await element.query_selector(".product-name p.semibold")
            price_el = await element.query_selector(".product-price")
            color_el = await element.query_selector(".product-color")
            img_el = await element.query_selector(".product-carousel img")
            link_el = await element.query_selector('a[href*="/products/"]')
            badge_el = await element.query_selector(".product-card-badge")

            name = await name_el.inner_text() if name_el else None
            if not name:
                return None

            # USD 가격 그대로 저장
            price_text = await price_el.inner_text() if price_el else "0"
            price_num = re.sub(r"[^\d.]", "", price_text.split("\n")[0])
            price = float(price_num) if price_num else 0

            color = await color_el.inner_text() if color_el else ""
            img_url = await img_el.get_attribute("src") if img_el else None
            if img_url and "_320x" in img_url:
                img_url = img_url.replace("_320x", "_600x")

            link = await link_el.get_attribute("href") if link_el else None
            product_url = f"{BASE_URL}{link}" if link and not link.startswith("http") else link

            badge_text = await badge_el.inner_text() if badge_el else ""

            # 상품 코드 추출
            code = ""
            if link:
                match = re.search(r"/products/([^/?]+)", link)
                if match:
                    code = match.group(1)
                else:
                    code = re.sub(r"[^a-zA-Z0-9]", "", name)[:30]

            category_id = self._url_to_category(page.url)

            tags = ["athleisure", "yoga"]
            if badge_text:
                tags.append(badge_text.lower().replace(" ", "-"))

            return {
                "id": self.make_product_id(code),
                "product_name": name.strip(),
                "product_name_kr": name.strip(),
                "price": price,
                "currency": "USD",
                "category_id": category_id,
                "season_id": "2026SS",
                "colors": [color.strip()] if color.strip() else [],
                "thumbnail_url": img_url,
                "image_urls": [img_url] if img_url else [],
                "product_url": product_url,
                "style_tags": tags,
            }
        except Exception as e:
            self.logger.warning(f"ALO parse error: {e}")
            return None

    async def parse_product_detail(self, page: Page, url: str) -> dict:
        """상품 상세 페이지에서 추가 정보 추출."""
        detail = {}
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)

            # 사이즈
            size_els = await page.query_selector_all(".button-size-selector__button")
            sizes = []
            for el in size_els:
                text = await el.inner_text()
                text = text.strip()
                if text:
                    sizes.append(text)
            if sizes:
                detail["sizes"] = sizes

            # 전체 컬러 (스워치에서 수집)
            all_colors = await page.evaluate("""() => {
                const colors = [];
                // swatch wrapper 안의 모든 스워치 링크
                const swatches = document.querySelectorAll('.swatches .swatch__wrapper a, .core-swatches a, .limited-swatches a');
                swatches.forEach(a => {
                    const title = a.getAttribute('title') || a.getAttribute('aria-label') || '';
                    if (title && !colors.includes(title)) colors.push(title);
                });
                if (colors.length === 0) {
                    // fallback: swatch labels
                    const labels = document.querySelectorAll('.swatch-label');
                    labels.forEach(s => {
                        const text = s.getAttribute('title') || s.innerText.trim();
                        if (text && !colors.includes(text)) colors.push(text);
                    });
                }
                if (colors.length === 0) {
                    // fallback: option-Color 안의 현재 컬러
                    const colorEl = document.querySelector('.option-Color .selected-option, .product-color');
                    if (colorEl) {
                        let text = colorEl.innerText.trim().replace(/^Color:\\s*/i, '');
                        if (text) colors.push(text);
                    }
                }
                // "Color: X" 접두어 제거
                return colors.map(c => c.replace(/^Color:\\s*/i, ''));
            }""")
            if all_colors:
                detail["colors"] = all_colors

            # 디스크립션 (FIT 섹션 분리)
            desc_el = await page.query_selector(".description")
            if desc_el:
                full_text = await desc_el.inner_text()
                full_text = full_text.strip()
                # DESCRIPTION / FIT / FABRICATION 섹션 분리
                desc_part = ""
                fit_part = ""
                sections = re.split(r"\n(?=DESCRIPTION|FIT|FABRICATION)", full_text)
                for section in sections:
                    s = section.strip()
                    if s.startswith("DESCRIPTION"):
                        desc_part = s.replace("DESCRIPTION", "", 1).strip()
                    elif s.startswith("FIT"):
                        fit_part = s.replace("FIT", "", 1).strip()
                if desc_part:
                    detail["description"] = desc_part
                elif not desc_part and full_text:
                    detail["description"] = full_text
                if fit_part:
                    detail["fit_info"] = fit_part

            # 소재 혼용률
            materials_data = await page.evaluate("""() => {
                const fabEl = document.querySelector('.fabrication');
                if (!fabEl) return {materials: [], desc: ''};
                const text = fabEl.innerText.trim();
                const lines = text.split('\\n');
                const materials = [];
                let desc = '';
                for (const line of lines) {
                    const t = line.trim();
                    if (!t || t.toUpperCase() === 'FABRICATION') continue;
                    if (t.match(/\\d+%/)) {
                        // "93% Modal, 7% Elastane" or "95% Nylon"
                        const parts = t.split(',');
                        for (const p of parts) {
                            const pt = p.trim();
                            if (pt.match(/\\d+%/)) materials.push(pt);
                        }
                    } else {
                        desc = t;
                    }
                }
                return {materials, desc};
            }""")
            if materials_data.get("materials"):
                detail["materials"] = materials_data["materials"]
            if materials_data.get("desc"):
                detail["fabric_desc"] = materials_data["desc"]

            # 핏 정보
            fit_text = await page.evaluate("""() => {
                // quickFitText 클래스
                const fitEl = document.querySelector('[class*="quickFitText"], [class*="fit-text"]');
                if (fitEl) return fitEl.innerText.trim();
                // description 안에서 "Fit:" 텍스트 찾기
                const desc = document.querySelector('.description');
                if (desc) {
                    const lines = desc.innerText.split('\\n');
                    for (const line of lines) {
                        if (line.match(/^Fit[:\\s]/i)) {
                            return line.replace(/^Fit[:\\s]+/i, '').trim();
                        }
                    }
                }
                // model description에서 핏 유추
                const modelEl = document.querySelector('.model-description');
                if (modelEl) return modelEl.innerText.trim();
                return '';
            }""")
            if fit_text:
                detail["fit_info"] = fit_text

        except Exception as e:
            self.logger.warning(f"Detail parse failed ({url}): {e}")

        return detail
