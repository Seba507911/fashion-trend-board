"""브랜드별 크롤러 설정.

플랫폼 기반 크롤러에 전달하는 config를 정의한다.
새 브랜드 추가 시 이 파일에 config만 추가하면 된다.

사용법:
    from backend.crawlers.brand_configs import get_crawler
    crawler = get_crawler("marithe")
    products = await crawler.crawl(fetch_details=True)
"""
from __future__ import annotations


# ─────────────────────────────────────────
# Cafe24 브랜드
# ─────────────────────────────────────────

CAFE24_BRANDS: dict[str, dict] = {
    "marithe": {
        "brand_id": "marithe",
        "base_url": "https://www.marithe-official.com",
        "categories": {
            "outer": ["815", "820"],
            "top": ["816", "821"],
            "bottom": ["817", "822"],
            "dress": ["818"],
            "accessories": ["819", "824"],
            "bag": ["823"],
        },
        "style_tags": ["french", "casual"],
        "season_id": "2026SS",
        "currency": "KRW",
    },
    "coor": {
        "brand_id": "coor",
        "base_url": "https://coor.kr",
        "categories": {
            "outer": ["25", "95", "92"],
            "top": ["56", "78", "85", "26", "76", "84"],
            "bottom": ["58", "79", "86"],
            "denim": ["53", "80", "87"],
            "skirt": ["102"],
            "bag": ["59", "81", "88"],
            "shoes": ["61", "82", "98"],
            "accessories": ["60", "83", "97"],
        },
        "style_tags": ["minimal", "contemporary"],
        "season_id": "2026SS",
        "currency": "KRW",
    },
    "blankroom": {
        "brand_id": "blankroom",
        "base_url": "https://blankroom.co.kr",
        "card_selector": "ul.thumbnail > li",
        "categories": {
            "outer": ["87", "103"],
            "top": ["30", "80", "107", "105"],
            "knit": ["51", "104"],
            "bottom": ["31", "106"],
            "denim": ["188", "187"],
            "skirt": ["240"],
            "bag": ["227"],
            "accessories": ["110"],
        },
        "style_tags": ["minimal", "contemporary"],
        "season_id": "2026SS",
        "currency": "KRW",
    },
    "youth": {
        "brand_id": "youth",
        "base_url": "https://youth-lab.kr",
        "categories": {
            "outer": ["150", "156"],
            "top": ["151", "157"],
            "bottom": ["152", "158"],
            "dress": ["162"],
            "denim": ["354", "355"],
            "bag": ["257", "270", "346"],
            "shoes": ["153", "159"],
            "accessories": ["154", "160"],
        },
        "style_tags": ["street", "casual"],
        "season_id": "2026SS",
        "currency": "KRW",
    },
}


# ─────────────────────────────────────────
# Shopify 브랜드
# ─────────────────────────────────────────

SHOPIFY_BRANDS: dict[str, dict] = {
    "alo": {
        "brand_id": "alo",
        "base_url": "https://www.aloyoga.com",
        "collections": {
            "tops": "top",
            "womens-jackets": "outer",
            "womens-leggings": "bottom",
            "pants": "bottom",
            "womens-sweatshirts-hoodies": "top",
            "shoes": "sneakers",
            "dresses": "dress",
            "accessories-shop-all": "etc_acc",
        },
        "card_selector": ".PlpTile",
        "selectors": {
            "name": ".product-name p.semibold",
            "price": ".product-price",
            "color": ".product-color",
            "image": ".product-carousel img",
            "link": "a[href*='/products/']",
        },
        "style_tags": ["athleisure", "yoga"],
        "currency": "USD",
        "season_id": "2026SS",
    },
    "lemaire": {
        "brand_id": "lemaire",
        "base_url": "https://lemaire.fr",
        "card_selector": "#product-grid > li",
        "selectors": {
            "name": ".card__heading a",
            "price": ".price-item--regular",
            "color": ".card__color",
            "image": ".card__media img",
            "link": ".card__media a[href], .card__heading a[href]",
        },
        "collections": {
            "women-coats": "outer",
            "women-jacket-outerwear": "outer",
            "men-coats": "outer",
            "women-tops": "top",
            "women-shirts": "top",
            "women-knitwear-and-jersey": "top",
            "men-tops": "top",
            "men-shirts": "top",
            "men-knitwear-and-jersey": "top",
            "women-pants": "bottom",
            "women-denim": "bottom",
            "men-pants": "bottom",
            "men-denim": "bottom",
            "skirts": "bottom",
            "dresses": "dress",
            "women-shoes": "shoes",
            "men-shoes": "shoes",
            "women-bags": "bag",
            "women-jewellery": "accessories",
            "women-accessories-all": "accessories",
        },
        "style_tags": ["minimal", "contemporary", "luxury"],
        "currency": "EUR",
        "season_id": "2026SS",
    },
}


# ─────────────────────────────────────────
# 커스텀 브랜드 (개별 크롤러 필요)
# ─────────────────────────────────────────

CUSTOM_BRANDS = ["newbalance", "asics", "northface", "descente"]


def get_crawler(brand_id: str):
    """브랜드 ID로 적절한 크롤러 인스턴스를 반환."""
    if brand_id in CAFE24_BRANDS:
        from backend.crawlers.platform_crawlers.cafe24 import Cafe24Crawler
        return Cafe24Crawler(CAFE24_BRANDS[brand_id])

    if brand_id in SHOPIFY_BRANDS:
        from backend.crawlers.platform_crawlers.shopify import ShopifyCrawler
        return ShopifyCrawler(SHOPIFY_BRANDS[brand_id])

    if brand_id == "newbalance":
        from backend.crawlers.brand_crawlers.newbalance import NewBalanceCrawler
        return NewBalanceCrawler()

    if brand_id == "asics":
        from backend.crawlers.brand_crawlers.asics import AsicsCrawler
        return AsicsCrawler()

    if brand_id == "northface":
        from backend.crawlers.brand_crawlers.northface import NorthFaceCrawler
        return NorthFaceCrawler()

    if brand_id == "descente":
        from backend.crawlers.brand_crawlers.descente import DescenteCrawler
        return DescenteCrawler()

    raise ValueError(f"Unknown brand: {brand_id}. "
                     f"Available: {list(CAFE24_BRANDS) + list(SHOPIFY_BRANDS) + CUSTOM_BRANDS}")


def list_brands() -> dict[str, str]:
    """등록된 브랜드 목록과 플랫폼 타입."""
    result = {}
    for b in CAFE24_BRANDS:
        result[b] = "cafe24"
    for b in SHOPIFY_BRANDS:
        result[b] = "shopify"
    for b in CUSTOM_BRANDS:
        result[b] = "custom"
    return result
