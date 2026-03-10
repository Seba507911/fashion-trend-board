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

            # ID: style_code만 사용 (컬러는 colors 배열에 저장)
            # NB는 컬러별로 style_code가 다를 수 있으므로 name+price 기반 dedup은 save_products에서 처리
            return {
                "id": self.make_product_id(style_code),
                "product_name": product_name,
                "product_name_kr": product_name,
                "price": nor_price if nor_price > 0 else price,
                "sale_price": sale_price,
                "currency": "KRW",
                "category_id": category_id,
                "season_id": "2026SS",
                "colors": [color_code] if color_code else [],
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

            info = await page.evaluate("""() => {
                const result = {sizes: [], colors: [], materials: [], description: '', imageUrls: []};

                // 사이즈: .size .items li input[name="pr_size"]
                const sizeInputs = document.querySelectorAll('.size .items li input[name="pr_size"], .size .items li input[type="radio"]');
                sizeInputs.forEach(inp => {
                    const info = inp.getAttribute('data-info') || inp.value || '';
                    if (info && !result.sizes.includes(info)) {
                        result.sizes.push(info);
                    }
                });

                // 컬러: .color .items li input[name="pr_color"]
                const colorInputs = document.querySelectorAll('.color .items li input[name="pr_color"], .color .items li input[type="radio"]');
                colorInputs.forEach(inp => {
                    const colorName = inp.getAttribute('data-info') || '';
                    if (colorName && !result.colors.includes(colorName)) {
                        result.colors.push(colorName);
                    }
                });

                // 설명: .detail__descContent
                const descEl = document.querySelector('.detail__descContent');
                if (descEl) {
                    const text = descEl.innerText.trim();
                    if (text.length > 10) result.description = text.substring(0, 500);
                }

                // 갤러리 이미지: swiper-slide img
                const galleryImgs = document.querySelectorAll('.swiper-slide img');
                const seenUrls = new Set();
                galleryImgs.forEach(img => {
                    const src = img.getAttribute('src') || '';
                    if (src && src.includes('NBRB_Product') && !seenUrls.has(src)) {
                        seenUrls.add(src);
                        result.imageUrls.push(src);
                    }
                });

                // 소재: AJAX 로딩이라 초기 HTML에 없을 수 있음
                // detail__listItem에서 시도
                const infoItems = document.querySelectorAll('.detail__listItem');
                infoItems.forEach(item => {
                    const label = item.querySelector('.detail__listTit');
                    const value = item.querySelector('.detail__listTxt');
                    if (label && value) {
                        const labelText = label.innerText.trim();
                        if (labelText.includes('소재') || labelText.includes('Material')) {
                            const matText = value.innerText.trim();
                            if (matText && matText.length > 2) {
                                result.materials.push(matText);
                            }
                        }
                    }
                });

                return result;
            }""")

            if info.get("sizes"):
                detail["sizes"] = info["sizes"]
            if info.get("colors"):
                detail["colors"] = info["colors"]
            if info.get("description"):
                detail["description"] = info["description"]
            if info.get("imageUrls"):
                detail["image_urls"] = info["imageUrls"]
            if info.get("materials"):
                detail["materials"] = info["materials"]

        except Exception as e:
            self.logger.warning(f"NB detail parse failed ({url}): {e}")

        return detail
