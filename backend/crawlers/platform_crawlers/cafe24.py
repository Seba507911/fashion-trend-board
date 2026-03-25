"""Cafe24 플랫폼 크롤러.

Cafe24 기반 쇼핑몰의 공통 크롤링 로직.
브랜드별로 config만 전달하면 동작한다.

지원 브랜드 예시: 마리떼, 마르디메크르디, 르블랑, 라이프워크 등

Config 형태:
    {
        "brand_id": "marithe",
        "base_url": "https://www.marithe-official.com",
        "categories": {
            "outer": ["815", "820"],    # cate_no 목록
            "top": ["816", "821"],
        },
        "style_tags": ["french", "casual"],
        "season_id": "2026SS",
        "currency": "KRW",
    }
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional

from playwright.async_api import Page

from backend.crawlers.base_crawler import BaseCrawler


class Cafe24Crawler(BaseCrawler):
    """Cafe24 플랫폼 공통 크롤러."""

    def __init__(self, config: dict):
        super().__init__(config["brand_id"])
        self.config = config
        self.base_url = config["base_url"].rstrip("/")
        self.categories = config.get("categories", {})
        self.style_tags = config.get("style_tags", [])
        self.season_id = config.get("season_id", "2026SS")
        self.currency = config.get("currency", "KRW")
        self._card_selector = config.get("card_selector", "ul.prdList > li.xans-record-")

        # cate_no → category 역매핑
        self._cate_map: dict[str, str] = {}
        for cat_id, cate_nos in self.categories.items():
            for cn in cate_nos:
                self._cate_map[str(cn)] = cat_id

    async def get_product_list_urls(self, season: Optional[str] = None) -> list[str]:
        urls = []
        for cate_nos in self.categories.values():
            for cn in cate_nos:
                urls.append(f"{self.base_url}/product/list.html?cate_no={cn}")
        return urls

    def get_card_selector(self) -> str:
        return self._card_selector

    def _url_to_category(self, page_url: str) -> Optional[str]:
        m = re.search(r"cate_no=(\d+)", page_url)
        if m:
            return self._cate_map.get(m.group(1))
        return None

    async def parse_product_card(self, page: Page, element) -> Optional[dict]:
        try:
            card_data = await element.evaluate("""(li) => {
                const result = {};
                result.productNo = (li.id || '').replace('anchorBoxId_', '');

                // 대표 이미지 — 품절 오버레이가 아닌 실제 상품 이미지 찾기
                const allImgs = li.querySelectorAll('.swiper-slide-active img, .swiper-slide:first-child img, .thumb img, .prdImg img, img.ThumbImage, .thumbnail img');
                result.imgSrc = '';
                for (const img of allImgs) {
                    const src = img.getAttribute('src') || img.getAttribute('data-src') || '';
                    if (src && !src.includes('ico_product_soldout') &&
                        !src.includes('btn_wish') &&
                        !src.includes('echosting.cafe24.com/design/skin')) {
                        result.imgSrc = src;
                        break;
                    }
                }

                const imgs = li.querySelectorAll('.swiper-slide img, .thumb img, img.ThumbImage, .thumbnail img');
                result.imageUrls = [];
                imgs.forEach(i => {
                    const src = i.getAttribute('src') || i.getAttribute('data-src') || '';
                    // 품절 오버레이/위시버튼 등 UI 이미지 필터링
                    if (src && !result.imageUrls.includes(src) &&
                        !src.includes('ico_product_soldout') &&
                        !src.includes('btn_wish') &&
                        !src.includes('ico_soldout') &&
                        !src.includes('btn_cart') &&
                        !src.includes('echosting.cafe24.com/design/skin')) {
                        result.imageUrls.push(src);
                    }
                });

                const nameEl = li.querySelector('.description .name a, .name a, .prd_name a, p.name a, .thumbnail-info .name a');
                result.href = nameEl ? nameEl.getAttribute('href') : '';
                result.name = nameEl ? nameEl.innerText.trim() : '';
                // Fallback: Emis 등 일부 사이트는 .name 안 span에 상품명이 있음
                if (!result.name) {
                    const nameSpan = li.querySelector('.name span[style], .name > span:not(.supplier):not(.icon):not(.srn-icon)');
                    if (nameSpan) result.name = nameSpan.innerText.trim();
                }
                // Name fallback: img alt attribute (DEPOUND 등)
                if (!result.name) {
                    const imgWithAlt = li.querySelector('img[alt]');
                    if (imgWithAlt && imgWithAlt.alt.length > 2) result.name = imgWithAlt.alt.trim();
                }
                // href fallback: thumb-box > a, prdImg > a
                if (!result.href) {
                    const thumbLink = li.querySelector('.thumb-box a[href*="product"], .prdImg a[href*="product"], a[href*="product_no"]');
                    if (thumbLink) result.href = thumbLink.getAttribute('href');
                }
                // productNo fallback: data-no attribute
                if (!result.productNo) {
                    result.productNo = li.getAttribute('data-no') || '';
                }
                // productNo fallback: href에서 product_no 추출
                if (!result.productNo && result.href) {
                    const m = result.href.match(/product_no=(\\d+)/) || result.href.match(/\\/(\\d+)\\//);
                    if (m) result.productNo = m[1];
                }

                const descEl = li.querySelector('.description[ec-data-price], [ec-data-price]');
                result.price = descEl ? descEl.getAttribute('ec-data-price') : '';

                const textContent = li.innerText || '';
                const priceMatches = textContent.match(/([\\d,]+)원/g);
                result.priceTexts = priceMatches || [];

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
            price = int(card_data["price"]) if card_data.get("price") else 0

            sale_price = None
            price_texts = card_data.get("priceTexts", [])
            if len(price_texts) >= 2:
                first = int(re.sub(r"[^\d]", "", price_texts[0]) or 0)
                second = int(re.sub(r"[^\d]", "", price_texts[1]) or 0)
                if second < first:
                    sale_price = second

            img_url = card_data.get("imgSrc", "")
            image_urls = card_data.get("imageUrls", [])

            href = card_data.get("href", "")
            product_url = href if href.startswith("http") else self.base_url + href

            category_id = self._url_to_category(page.url)
            sizes = card_data.get("sizes", [])

            # 상품명에서 컬러 추출 + base name 분리
            base_name, colors = self._extract_and_strip_color(product_name)

            return {
                "id": self.make_product_id(product_no),
                "product_name": base_name,
                "product_name_kr": base_name,
                "price": price,
                "sale_price": sale_price,
                "currency": self.currency,
                "category_id": category_id,
                "season_id": self.season_id,
                "colors": colors,
                "sizes": sizes,
                "thumbnail_url": img_url,
                "image_urls": image_urls[:5],
                "product_url": product_url,
                "style_tags": self.style_tags,
            }
        except Exception as e:
            self.logger.warning(f"Cafe24 card parse error: {e}")
            return None

    async def parse_product_detail(self, page: Page, url: str) -> dict:
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

                // 상세 설명 — 실제 상품 설명 영역만 수집 (결제/배송 안내 제외)
                // 우선순위: 전용 description 셀렉터 → .cont 에서 결제 안내 필터링
                const descCandidates = [
                    '.prd_detail_basic', '.product-detail', '#prdDetail',
                    '.cont', '.product_detail', '.detail_cont'
                ];
                let contText = '';
                for (const sel of descCandidates) {
                    const el = document.querySelector(sel);
                    if (el) {
                        const text = el.innerText.trim();
                        // 결제/배송/교환/반품 안내가 아닌 실제 상품 설명인지 확인
                        if (text.length > 10 && !text.startsWith('상품결제정보') &&
                            !text.startsWith('배송정보') && !text.startsWith('교환') &&
                            !text.startsWith('고액결제') && text.indexOf('카드사에서 확인전화') === -1) {
                            contText = text;
                            break;
                        }
                    }
                }
                result.description = '';
                result.materials = [];
                result.fitInfo = '';

                if (contText) {
                    const matLines = contText.match(/[가-힣A-Za-z]+\\s*\\d+%/g);
                    if (matLines) result.materials = [...new Set(matLines)];
                    const matLines2 = contText.match(/\\d+%\\s*[가-힣A-Za-z]+/g);
                    if (matLines2) {
                        matLines2.forEach(m => {
                            if (!result.materials.includes(m)) result.materials.push(m);
                        });
                    }

                    // 결제/배송/교환/반품 안내 부분 제거
                    const cutPatterns = ['상품결제정보', '배송정보', '교환 및 반품', 'SIZE GUIDE'];
                    let descEnd = contText.length;
                    for (const pat of cutPatterns) {
                        const idx = contText.indexOf(pat);
                        if (idx > 0 && idx < descEnd) descEnd = idx;
                    }
                    result.description = contText.substring(0, Math.min(descEnd, 500)).trim();
                    const sizeIdx = contText.indexOf('SIZE GUIDE');
                    if (sizeIdx > 0) {
                        result.fitInfo = contText.substring(sizeIdx).trim().substring(0, 500);
                    }
                }

                // 컬러 — 관련 상품에서 추출
                result.colors = [];
                const relatedEls = document.querySelectorAll(
                    '.xans-product-relation .name a, .relation_prd .name a'
                );
                relatedEls.forEach(el => {
                    const text = el.innerText.trim();
                    if (text) {
                        const parts = text.split(' ');
                        if (parts.length > 1) result.colors.push(parts[parts.length - 1]);
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
            self.logger.warning(f"Cafe24 detail parse failed ({url}): {e}")

        return detail

    # 영문 컬러 키워드 (긴 것부터 매칭)
    _EN_COLORS = sorted([
        "light heather gray", "light heather grey", "heather gray", "heather grey",
        "deep navy", "dark navy", "light grey", "light gray", "dark gray", "dark grey",
        "melange gray", "melange grey", "sky blue", "dusty pink", "off white",
        "black chocolate", "midnight brown",
        "black", "white", "navy", "gray", "grey", "cream", "beige", "brown", "blue",
        "red", "green", "pink", "yellow", "orange", "purple", "khaki", "ivory",
        "charcoal", "olive", "mint", "lavender", "sand", "camel", "oatmeal",
        "burgundy", "wine", "coral", "peach", "sage", "taupe", "mocha", "espresso",
        "denim", "indigo", "mauve", "rose", "ecru", "natural", "teal", "cobalt",
        "lime", "stone",
    ], key=len, reverse=True)

    # 한글 컬러 키워드
    _KR_COLORS = sorted([
        "프렌치블루", "딥블루그레이", "블루그레이", "다크브라운", "딥네이비",
        "다크그레이", "라이트그레이", "라이트베이지", "웜베이지", "올리브카키",
        "베이지", "블랙", "네이비", "브라운", "그레이", "화이트", "아이보리",
        "카키", "올리브", "차콜", "크림", "와인", "버건디", "핑크", "레드",
        "블루", "그린", "옐로우", "오렌지", "퍼플", "민트", "라벤더",
        "카멜", "모카", "샌드", "오트밀", "인디고", "데님", "코발트",
    ], key=len, reverse=True)

    def _extract_and_strip_color(self, product_name: str) -> tuple[str, list[str]]:
        """상품명에서 컬러를 추출하고 제거한 base name 반환.

        Returns:
            (base_name, [color]) — 컬러가 없으면 (원래 이름, [])
        """
        lower = product_name.lower().strip()

        # 1. 영문 suffix: "CLASSIC LOGO TEE black"
        for cw in self._EN_COLORS:
            if lower.endswith(" " + cw):
                base = product_name[: len(product_name) - len(cw)].strip()
                color = product_name[len(base):].strip()
                return base, [color]

        # 2. 한글 괄호: "팬츠 (프렌치블루)"
        m = re.search(r"\s*\(([^)]+)\)\s*$", product_name)
        if m:
            candidate = m.group(1).strip()
            for kc in self._KR_COLORS:
                if kc in candidate:
                    base = product_name[: m.start()].strip()
                    return base, [candidate]

        # 3. 언더스코어: "JACKET_BLACK"
        if "_" in product_name:
            base, color_part = product_name.rsplit("_", 1)
            color_lower = color_part.strip().lower()
            cat_words = {"pants", "shirt", "skirt", "bag", "belt", "coat",
                         "jacket", "blouson", "knit", "top", "neck", "scarf",
                         "sleeveless", "flare", "jumper", "vest"}
            first_word = color_lower.split()[0] if color_part.split() else ""
            if first_word not in cat_words:
                for ec in self._EN_COLORS:
                    if ec in color_lower:
                        return base.strip(), [color_part.strip()]

        return product_name, []
