"""New Balance Korea 공식몰 크롤러.

대상: https://www.nbkorea.com/
카테고리: /product/productList.action?cateGrpCode=250110&cIdx=XXXX
상품 카드: data-* 속성으로 정보 제공 (JS 기반 네비게이션)
상세 URL: /product/productDetail.action?styleCode=XXX&colorCode=YY
"""
import asyncio
import re
from typing import Optional

from playwright.async_api import Page

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.nbkorea.com"

# cIdx → 카테고리 매핑
CATEGORY_URLS = {
    "sneakers": f"{BASE_URL}/product/productList.action?cateGrpCode=250110&cIdx=1280",
    "outer": f"{BASE_URL}/product/productList.action?cateGrpCode=250110&cIdx=1293",
    "top": f"{BASE_URL}/product/productList.action?cateGrpCode=250110&cIdx=1294",
    "bottom": f"{BASE_URL}/product/productList.action?cateGrpCode=250110&cIdx=2377",
    "bag": f"{BASE_URL}/product/productList.action?cateGrpCode=250110&cIdx=1299",
    "hat": f"{BASE_URL}/product/productList.action?cateGrpCode=250110&cIdx=1300",
}


class NewBalanceCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("newbalance")

    async def get_product_list_urls(self, season: Optional[str] = None) -> list[str]:
        return list(CATEGORY_URLS.values())

    def get_card_selector(self) -> str:
        return ".prdName"

    def _url_to_category(self, page_url: str) -> Optional[str]:
        """URL의 cIdx로 카테고리 매핑."""
        for cat_id, cat_url in CATEGORY_URLS.items():
            cIdx = re.search(r"cIdx=(\d+)", cat_url)
            if cIdx and cIdx.group(1) in page_url:
                return cat_id
        return None

    async def parse_product_card(self, page: Page, element) -> Optional[dict]:
        try:
            # 부모 li > a#selDetail 에서 data 속성 추출
            parent_li = await element.evaluate_handle("el => el.closest('li')")
            link_el = await parent_li.query_selector("a#selDetail, a.pro_area")

            if not link_el:
                return None

            style_code = await link_el.get_attribute("data-style") or ""
            color_code = await link_el.get_attribute("data-color") or ""
            display_name = await link_el.get_attribute("data-display-name") or ""
            price_text = await link_el.get_attribute("data-price") or "0"
            nor_price_text = await link_el.get_attribute("data-nor-price") or "0"

            if not display_name or not style_code:
                return None

            price = int(re.sub(r"[^\d]", "", price_text) or 0)
            nor_price = int(re.sub(r"[^\d]", "", nor_price_text) or 0)
            sale_price = price if price < nor_price else None

            # 이미지
            img_el = await parent_li.query_selector("img#selGoods, img")
            img_url = await img_el.get_attribute("src") if img_el else None

            # 상세 페이지 URL
            product_url = f"{BASE_URL}/product/productDetail.action?styleCode={style_code}&colorCode={color_code}"

            # 상품명 정리 ("NB | XXX" → "XXX")
            product_name = display_name.strip()
            if "|" in product_name:
                product_name = product_name.split("|", 1)[1].strip()

            category_id = self._url_to_category(page.url)

            return {
                "id": self.make_product_id(f"{style_code}_{color_code}"),
                "product_name": product_name,
                "product_name_kr": product_name,
                "price": nor_price if nor_price > 0 else price,
                "sale_price": sale_price,
                "currency": "KRW",
                "category_id": category_id,
                "season_id": "2026SS",
                "colors": [],
                "thumbnail_url": img_url,
                "image_urls": [img_url] if img_url else [],
                "product_url": product_url,
                "style_tags": ["lifestyle"],
            }
        except Exception as e:
            self.logger.warning(f"NB parse error: {e}")
            return None

    async def parse_product_detail(self, page: Page, url: str) -> dict:
        """상품 상세 페이지에서 추가 정보 추출."""
        detail = {}
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)

            # 사이즈
            sizes = await page.evaluate("""() => {
                const sizeEls = document.querySelectorAll('.size_list li a, .sizeList li a, [class*="size"] li a, .opt_size li a');
                const sizes = [];
                sizeEls.forEach(el => {
                    const text = el.innerText.trim();
                    if (text && text !== '사이즈' && !text.includes('선택')) sizes.push(text);
                });
                return sizes;
            }""")
            if sizes:
                detail["sizes"] = sizes

            # 컬러
            colors = await page.evaluate("""() => {
                const colors = [];
                const imgs = document.querySelectorAll('.color_list img, .colorChip img, [class*="color"] img');
                imgs.forEach(img => {
                    const alt = img.getAttribute('alt') || '';
                    if (alt && !colors.includes(alt)) colors.push(alt);
                });
                if (colors.length === 0) {
                    const colorEls = document.querySelectorAll('.color_list li a, [class*="color"] li a');
                    colorEls.forEach(el => {
                        const title = el.getAttribute('title') || el.getAttribute('data-color-name') || el.innerText.trim();
                        if (title && !colors.includes(title)) colors.push(title);
                    });
                }
                return colors;
            }""")
            if colors:
                detail["colors"] = colors

            # 상세 정보 (소재, 설명)
            info = await page.evaluate("""() => {
                const result = {description: '', materials: [], fit_info: ''};
                const descEl = document.querySelector('.prd_detail_info, .detail_info, .product_info');
                if (descEl) result.description = descEl.innerText.trim().substring(0, 500);
                // 소재: 전체 텍스트에서 "% 소재" 패턴 추출
                const allText = document.body.innerText;
                const matMatches = allText.match(/\\d+%\\s*[가-힣A-Za-z]+/g);
                if (matMatches) {
                    result.materials = [...new Set(matMatches)].slice(0, 5);
                }
                return result;
            }""")
            if info.get("description"):
                detail["description"] = info["description"]
            if info.get("materials"):
                detail["materials"] = info["materials"]

        except Exception as e:
            self.logger.warning(f"NB detail parse failed ({url}): {e}")

        return detail
