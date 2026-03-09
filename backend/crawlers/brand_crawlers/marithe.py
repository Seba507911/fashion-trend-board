"""마리떼 프랑소와 저버 공식몰 크롤러.

대상: https://www.marithe-official.com/ (Cafe24 기반)
카테고리: /product/list.html?cate_no=XXX
상품 카드: ul.prdList > li.xans-record- (description 영역에 이름/가격)
상세 URL: /product/{slug}/{product_no}/category/{cate_no}/display/1/
"""
import asyncio
import re
from typing import Optional

from playwright.async_api import Page

from backend.crawlers.base_crawler import BaseCrawler

BASE_URL = "https://www.marithe-official.com"

# 여성/남성 카테고리
CATEGORY_URLS = {
    "outer": [
        f"{BASE_URL}/product/list.html?cate_no=815",   # 여성 아우터
        f"{BASE_URL}/product/list.html?cate_no=820",   # 남성 아우터
    ],
    "top": [
        f"{BASE_URL}/product/list.html?cate_no=816",   # 여성 상의
        f"{BASE_URL}/product/list.html?cate_no=821",   # 남성 상의
    ],
    "bottom": [
        f"{BASE_URL}/product/list.html?cate_no=817",   # 여성 하의
        f"{BASE_URL}/product/list.html?cate_no=822",   # 남성 하의
    ],
    "dress": [
        f"{BASE_URL}/product/list.html?cate_no=818",   # 여성 세트/원피스
    ],
    "accessories": [
        f"{BASE_URL}/product/list.html?cate_no=819",   # 여성 액세서리
        f"{BASE_URL}/product/list.html?cate_no=824",   # 남성 액세서리
    ],
    "bag": [
        f"{BASE_URL}/product/list.html?cate_no=823",   # 남성 가방
    ],
}

# cate_no → category 역매핑
CATE_NO_MAP = {
    "815": "outer", "820": "outer",
    "816": "top", "821": "top",
    "817": "bottom", "822": "bottom",
    "818": "dress",
    "819": "accessories", "824": "accessories",
    "823": "bag",
}


class MaritheCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("marithe")

    async def get_product_list_urls(self, season: Optional[str] = None) -> list[str]:
        urls = []
        for cat_urls in CATEGORY_URLS.values():
            urls.extend(cat_urls)
        return urls

    def get_card_selector(self) -> str:
        return "ul.prdList > li.xans-record-"

    def _url_to_category(self, page_url: str) -> Optional[str]:
        """URL의 cate_no로 카테고리 매핑."""
        m = re.search(r"cate_no=(\d+)", page_url)
        if m:
            return CATE_NO_MAP.get(m.group(1))
        return None

    async def parse_product_card(self, page: Page, element) -> Optional[dict]:
        try:
            card_data = await element.evaluate("""(li) => {
                const result = {};

                // product_no from li id (anchorBoxId_14085 → 14085)
                result.productNo = (li.id || '').replace('anchorBoxId_', '');

                // 이미지
                const img = li.querySelector('.swiper-slide-active img, .swiper-slide:first-child img');
                result.imgSrc = img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : '';

                // 추가 이미지들
                const imgs = li.querySelectorAll('.swiper-slide img');
                result.imageUrls = [];
                imgs.forEach(i => {
                    const src = i.getAttribute('src') || i.getAttribute('data-src') || '';
                    if (src && !result.imageUrls.includes(src)) result.imageUrls.push(src);
                });

                // 상품 링크 & 이름
                const nameEl = li.querySelector('.description .name a');
                result.href = nameEl ? nameEl.getAttribute('href') : '';
                result.name = nameEl ? nameEl.innerText.trim() : '';

                // 가격 (ec-data-price 속성)
                const descEl = li.querySelector('.description[ec-data-price]');
                result.price = descEl ? descEl.getAttribute('ec-data-price') : '';

                // 할인가 텍스트에서 추출
                const textContent = li.innerText || '';
                const priceMatches = textContent.match(/([\\d,]+)원/g);
                result.priceTexts = priceMatches || [];

                // 사이즈 (option_layer에서)
                const sizeEls = li.querySelectorAll('.option_layer li span');
                result.sizes = [];
                sizeEls.forEach(el => {
                    const text = el.innerText.trim();
                    if (text) result.sizes.push(text);
                });

                return result;
            }""")

            if not card_data.get("name") or not card_data.get("productNo"):
                return None

            product_no = card_data["productNo"]
            product_name = card_data["name"]

            # 가격
            price = int(card_data["price"]) if card_data.get("price") else 0

            # 할인가: 가격 텍스트에서 두번째 값이 있으면 할인가
            sale_price = None
            price_texts = card_data.get("priceTexts", [])
            if len(price_texts) >= 2:
                first = int(re.sub(r"[^\d]", "", price_texts[0]) or 0)
                second = int(re.sub(r"[^\d]", "", price_texts[1]) or 0)
                if second < first:
                    sale_price = second

            # 이미지
            img_url = card_data.get("imgSrc", "")
            image_urls = card_data.get("imageUrls", [])

            # 상품 URL
            href = card_data.get("href", "")
            product_url = href if href.startswith("http") else BASE_URL + href

            # 카테고리
            category_id = self._url_to_category(page.url)

            # 사이즈
            sizes = card_data.get("sizes", [])

            # 상품명에서 컬러 추출
            colors = []
            name_parts = product_name.rsplit(" ", 1)
            if len(name_parts) == 2:
                possible_color = name_parts[1].lower()
                color_keywords = [
                    "white", "black", "gray", "grey", "navy", "blue", "red",
                    "pink", "green", "yellow", "beige", "brown", "cream",
                    "olive", "charcoal", "mint", "ivory", "khaki", "orange",
                    "purple", "lavender", "violet", "sand", "camel",
                ]
                if possible_color in color_keywords:
                    colors = [name_parts[1]]

            return {
                "id": self.make_product_id(product_no),
                "product_name": product_name,
                "product_name_kr": product_name,
                "price": price,
                "sale_price": sale_price,
                "currency": "KRW",
                "category_id": category_id,
                "season_id": "2026SS",
                "colors": colors,
                "sizes": sizes,
                "thumbnail_url": img_url,
                "image_urls": image_urls[:5],
                "product_url": product_url,
                "style_tags": ["french", "casual"],
            }
        except Exception as e:
            self.logger.warning(f"Marithe parse error: {e}")
            return None

    async def parse_product_detail(self, page: Page, url: str) -> dict:
        """상품 상세 페이지에서 추가 정보 추출."""
        detail = {}
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)

            info = await page.evaluate("""() => {
                const result = {};

                // 사이즈 (select option)
                const sizeOpts = document.querySelectorAll('select[name="option1"] option');
                result.sizes = [];
                sizeOpts.forEach(o => {
                    const text = o.innerText.trim();
                    if (text && text !== 'empty' && !text.includes('선택') &&
                        !text.includes('필수') && text !== '---') {
                        const clean = text.replace(/\\s*\\[.*\\]/, '').trim();
                        if (clean) result.sizes.push(clean);
                    }
                });

                // 상세 설명 (.cont 영역)
                const contEl = document.querySelector('.cont');
                const contText = contEl ? contEl.innerText.trim() : '';
                result.fullText = contText;

                result.description = '';
                result.materials = [];
                result.fitInfo = '';

                if (contText) {
                    // 소재: "나일론 100%", "면 80%" 등
                    const matLines = contText.match(/[가-힣A-Za-z]+\\s*\\d+%/g);
                    if (matLines) result.materials = [...new Set(matLines)];
                    const matLines2 = contText.match(/\\d+%\\s*[가-힣A-Za-z]+/g);
                    if (matLines2) {
                        matLines2.forEach(m => {
                            if (!result.materials.includes(m)) result.materials.push(m);
                        });
                    }

                    // SIZE GUIDE 이전까지가 설명
                    const sizeIdx = contText.indexOf('SIZE GUIDE');
                    if (sizeIdx > 0) {
                        result.description = contText.substring(0, sizeIdx).trim();
                    } else {
                        result.description = contText.substring(0, 500);
                    }

                    // SIZE GUIDE에서 핏 정보 추출
                    if (sizeIdx > 0) {
                        result.fitInfo = contText.substring(sizeIdx).trim().substring(0, 500);
                    }
                }

                // 컬러 - 관련 상품에서 컬러 추출
                result.colors = [];
                const relatedEls = document.querySelectorAll('.xans-product-relation .name a, .relation_prd .name a, .xans-product-mobilerelation .name a');
                relatedEls.forEach(el => {
                    const text = el.innerText.trim();
                    if (text) {
                        const parts = text.split(' ');
                        if (parts.length > 1) {
                            result.colors.push(parts[parts.length - 1]);
                        }
                    }
                });

                return result;
            }""")

            if info.get("sizes"):
                detail["sizes"] = info["sizes"]
            if info.get("materials"):
                detail["materials"] = [
                    m for m in info["materials"]
                    if "쿠폰" not in m and "적립" not in m and "할인" not in m
                ]
            if info.get("description"):
                detail["description"] = info["description"]
            if info.get("fitInfo"):
                detail["fit_info"] = info["fitInfo"]
            if info.get("colors"):
                detail["colors"] = list(set(info["colors"]))

        except Exception as e:
            self.logger.warning(f"Marithe detail parse failed ({url}): {e}")

        return detail
