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
            "inner": ["816", "821"],
            "bottom": ["817", "822"],
            "wear_etc": ["818"],
            "acc_etc": ["819", "824"],
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
            "inner": ["56", "78", "85", "26", "76", "84"],
            "bottom": ["58", "79", "86"],
            "bottom": ["53", "80", "87"],
            "bottom": ["102"],
            "bag": ["59", "81", "88"],
            "shoes": ["61", "82", "98"],
            "acc_etc": ["60", "83", "97"],
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
            "inner": ["30", "80", "107", "105"],
            "knit": ["51", "104"],
            "bottom": ["31", "106"],
            "bottom": ["188", "187"],
            "bottom": ["240"],
            "bag": ["227"],
            "acc_etc": ["110"],
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
            "inner": ["151", "157"],
            "bottom": ["152", "158"],
            "wear_etc": ["162"],
            "bottom": ["354", "355"],
            "bag": ["257", "270", "346"],
            "shoes": ["153", "159"],
            "acc_etc": ["154", "160"],
        },
        "style_tags": ["street", "casual"],
        "season_id": "2026SS",
        "currency": "KRW",
    },
    "mardi": {
        "brand_id": "mardi",
        "base_url": "https://www.mardimercredi.com",
        "categories": {
            "outer": ["524"],
            "inner": ["519", "520", "521", "522", "523"],
            "bottom": ["525"],
            "wear_etc": ["526"],
            "bag": ["528"],
            "shoes": ["553"],
            "acc_etc": ["527"],
        },
        "style_tags": ["french", "casual", "logo"],
        "season_id": "2026SS",
        "currency": "KRW",
    },
    "emis": {
        "brand_id": "emis",
        "base_url": "https://emis.kr",
        "card_selector": ".prdList li.xans-record-",
        "categories": {
            "inner": ["52"],
            "headwear": ["49"],
            "bag": ["42"],
            "acc_etc": ["43"],
        },
        "style_tags": ["casual", "accessories"],
        "season_id": "2026SS",
        "currency": "KRW",
    },
    "dunst": {
        "brand_id": "dunst",
        "base_url": "https://dunststudio.com",
        "card_selector": "li.xans-record-",
        "categories": {
            "outer": ["29"],
            "inner": ["30", "31"],
            "bottom": ["32", "33"],
            "wear_etc": ["34"],
            "acc_etc": ["303"],
        },
        "style_tags": ["minimal", "contemporary", "unisex"],
        "season_id": "2026SS",
        "currency": "KRW",
    },
    "amomento": {
        "brand_id": "amomento",
        "base_url": "https://www.shopamomento.com",
        "card_selector": "li.xans-record-",
        "categories": {
            "outer": ["125"],
            "inner": ["129", "131"],
            "bottom": ["171"],
            "wear_etc": ["196"],
            "acc_etc": ["249", "261"],
        },
        "style_tags": ["minimal", "contemporary"],
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
            "tops": "inner",
            "womens-jackets": "outer",
            "womens-leggings": "bottom",
            "pants": "bottom",
            "womens-sweatshirts-hoodies": "inner",
            "shoes": "shoes",
            "dresses": "wear_etc",
            "accessories-shop-all": "acc_etc",
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
            "women-tops": "inner",
            "women-shirts": "inner",
            "women-knitwear-and-jersey": "inner",
            "men-tops": "inner",
            "men-shirts": "inner",
            "men-knitwear-and-jersey": "inner",
            "women-pants": "bottom",
            "women-denim": "bottom",
            "men-pants": "bottom",
            "men-denim": "bottom",
            "skirts": "bottom",
            "dresses": "wear_etc",
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
    "stussy": {
        "brand_id": "stussy",
        "base_url": "https://www.stussy.com",
        "card_selector": ".product-card, .collection-product",
        "selectors": {
            "name": ".product-card__title, .product-name",
            "price": ".product-card__price, .product-price",
            "color": ".product-card__color",
            "image": ".product-card__image img, .product-media img",
            "link": "a[href*='/products/']",
        },
        "collections": {
            "outerwear": "outer",
            "tops-shirts": "inner",
            "tees": "inner",
            "crew-sweats": "inner",
            "hoodies": "inner",
            "knits": "inner",
            "pants": "bottom",
            "shorts": "bottom",
            "bottom": "bottom",
            "headwear": "headwear",
            "acc_etc": "acc_etc",
        },
        "style_tags": ["street", "surf", "skate"],
        "currency": "USD",
        "season_id": "2026SS",
    },
    # ami, bode, skims: moved to custom crawlers
    "depound": {
        "brand_id": "depound",
        "base_url": "https://depound.com",
        "card_selector": "li.item.xans-record-",
        "categories": {
            "bag": ["100", "101"],
            "acc_etc": ["117", "131", "132", "133", "134", "137"],
        },
        "style_tags": ["minimal", "accessories", "bag"],
        "season_id": "2026SS",
        "currency": "KRW",
    },
    "nanushka": {
        "brand_id": "nanushka",
        "base_url": "https://nanushka.com",
        "card_selector": ".product-card, .grid__item",
        "selectors": {
            "name": ".product-card__title, .card__heading a, h3 a",
            "price": ".product-card__price, .price, .price-item",
            "image": ".product-card img, .card__media img",
            "link": "a[href*='/products/']",
        },
        "collections": {
            "fall-winter-2025-womenswear": "inner",
            "fall-winter-2025-menswear": "inner",
            "bags": "bag",
            "all-accessories": "acc_etc",
            "eyewear": "acc_etc",
        },
        "style_tags": ["sustainable", "contemporary", "luxury"],
        "currency": "USD",
        "season_id": "2026SS",
    },
    "toteme": {
        "brand_id": "toteme",
        "base_url": "https://www.toteme-studio.com",
        "card_selector": ".product-card, .grid__item",
        "selectors": {
            "name": ".product-card__title, .card__heading a, h3 a",
            "price": ".product-card__price, .price, .price-item",
            "image": ".product-card img, .card__media img",
            "link": "a[href*='/products/']",
        },
        "collections": {
            "blazers": "outer",
            "coats": "outer",
            "jackets": "outer",
            "knitwear": "inner",
            "t-shirts-tops": "inner",
            "shirts": "inner",
            "trousers": "bottom",
            "denim": "bottom",
            "skirts": "bottom",
            "dresses": "wear_etc",
            "bags": "bag",
            "shoes": "shoes",
        },
        "style_tags": ["scandi", "minimal", "contemporary"],
        "currency": "EUR",
        "season_id": "2026SS",
    },
    "therow": {
        "brand_id": "therow",
        "base_url": "https://www.therow.com",
        "card_selector": ".product-card, .grid__item",
        "selectors": {
            "name": ".product-card__title, .card__heading a, h3 a",
            "price": ".product-card__price, .price, .price-item",
            "image": ".product-card img, .card__media img",
            "link": "a[href*='/products/']",
        },
        "collections": {
            "men-coats-outerwear": "outer",
            "men-knitwear": "inner",
            "men-tops": "inner",
            "men-shirts": "inner",
            "men-pants": "bottom",
            "men-denim": "bottom",
            "men-shoes": "shoes",
            "women-coats-outerwear": "outer",
            "women-knitwear": "inner",
            "women-tops": "inner",
            "women-pants": "bottom",
            "women-dresses": "wear_etc",
            "handbags-new-arrivals": "bag",
        },
        "style_tags": ["ultra-luxury", "minimal", "quiet-luxury"],
        "currency": "USD",
        "season_id": "2026SS",
    },
    "fila": {
        "brand_id": "fila",
        "base_url": "https://www.fila.co.kr",
        "card_selector": ".product-card, .card-product, .product-card-wrapper",
        "selectors": {
            "name": ".product-card__title, .card__heading a, h3 a",
            "price": ".product-card__price, .price, .price-item",
            "color": ".product-card__color",
            "image": ".product-card__image img, .card__media img, img.motion-reduce",
            "link": "a[href*='/products/']",
        },
        "collections": {
            "%EB%B0%94%EB%9E%8C%EB%A7%89%EC%9D%B4-%EC%A7%91%EC%97%85-%EB%82%A8%EC%84%B1-%EC%9D%98%EB%A5%98": "outer",
            "%EB%B0%94%EB%9E%8C%EB%A7%89%EC%9D%B4-%EC%A7%91%EC%97%85-%EC%97%AC%EC%84%B1-%EC%9D%98%EB%A5%98": "outer",
            "%EB%B0%98%ED%8C%94-%EB%82%A8%EC%84%B1-%EC%9D%98%EB%A5%98": "inner",
            "%EA%B8%B4%ED%8C%94-%EB%82%A8%EC%84%B1-%EC%9D%98%EB%A5%98": "inner",
            "%EB%A7%A8%ED%88%AC%EB%A7%A8-%ED%9B%84%EB%94%94-%EB%82%A8%EC%84%B1-%EC%9D%98%EB%A5%98": "inner",
            "%EB%B0%98%ED%8C%94-%EC%97%AC%EC%84%B1-%EC%9D%98%EB%A5%98": "inner",
            "%EA%B8%B4%ED%8C%94-%EC%97%AC%EC%84%B1-%EC%9D%98%EB%A5%98": "inner",
            "%EB%9F%AC%EB%8B%9D-%EB%82%A8%EC%84%B1-%EC%8B%A0%EB%B0%9C": "shoes",
            "%EB%9F%AC%EB%8B%9D-%EC%97%AC%EC%84%B1-%EC%8B%A0%EB%B0%9C": "shoes",
            "%EB%9D%BC%EC%9D%B4%ED%94%84%EC%8A%A4%ED%83%80%EC%9D%BC-%EB%82%A8%EC%84%B1-%EC%8B%A0%EB%B0%9C": "shoes",
            "%EB%9D%BC%EC%9D%B4%ED%94%84%EC%8A%A4%ED%83%80%EC%9D%BC-%EC%97%AC%EC%84%B1-%EC%8B%A0%EB%B0%9C": "shoes",
            "%EB%AA%A8%EC%9E%90-%EB%82%A8%EC%84%B1-%EC%9A%A9%ED%92%88": "headwear",
            "%EB%A9%94%EC%8B%A0%EC%A0%80-%ED%81%AC%EB%A1%9C%EC%8A%A4%EB%B0%B1-%EB%82%A8%EC%84%B1-%EC%9A%A9%ED%92%88": "bag",
        },
        "style_tags": ["retro", "sportswear"],
        "currency": "KRW",
        "season_id": "2026SS",
    },
}


# ─────────────────────────────────────────
# 커스텀 브랜드 (개별 크롤러 필요)
# ─────────────────────────────────────────

CUSTOM_BRANDS = [
    "newbalance", "asics", "northface", "descente", "nike", "kolonsport",
    "lululemon", "acne_studios", "zara", "hm",
    "maison_kitsune", "ami", "ralph_lauren", "thisisneverthat", "on_running",
    "nanamica", "supreme", "bode", "skims",
    "nanushka", "patagonia", "human_made",
]


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

    if brand_id == "nike":
        from backend.crawlers.brand_crawlers.nike import NikeCrawler
        return NikeCrawler()

    if brand_id == "kolonsport":
        from backend.crawlers.brand_crawlers.kolonsport import KolonSportCrawler
        return KolonSportCrawler()

    if brand_id == "lululemon":
        from backend.crawlers.brand_crawlers.lululemon import LululemonCrawler
        return LululemonCrawler()

    if brand_id == "acne_studios":
        from backend.crawlers.brand_crawlers.acne_studios import AcneStudiosCrawler
        return AcneStudiosCrawler()

    if brand_id == "zara":
        from backend.crawlers.brand_crawlers.zara import ZaraCrawler
        return ZaraCrawler()

    if brand_id == "hm":
        from backend.crawlers.brand_crawlers.hm import HMCrawler
        return HMCrawler()

    if brand_id == "maison_kitsune":
        from backend.crawlers.brand_crawlers.maison_kitsune import MaisonKitsuneCrawler
        return MaisonKitsuneCrawler()

    if brand_id == "ami":
        from backend.crawlers.brand_crawlers.ami import AmiCrawler
        return AmiCrawler()

    if brand_id == "ralph_lauren":
        from backend.crawlers.brand_crawlers.ralph_lauren import RalphLaurenCrawler
        return RalphLaurenCrawler()

    if brand_id == "thisisneverthat":
        from backend.crawlers.brand_crawlers.thisisneverthat import ThisisneverthatCrawler
        return ThisisneverthatCrawler()

    if brand_id == "on_running":
        from backend.crawlers.brand_crawlers.on_running import OnRunningCrawler
        return OnRunningCrawler()

    if brand_id == "nanamica":
        from backend.crawlers.brand_crawlers.nanamica import NanamicaCrawler
        return NanamicaCrawler()

    if brand_id == "supreme":
        from backend.crawlers.brand_crawlers.supreme import SupremeCrawler
        return SupremeCrawler()

    if brand_id == "bode":
        from backend.crawlers.brand_crawlers.bode import BodeCrawler
        return BodeCrawler()

    if brand_id == "skims":
        from backend.crawlers.brand_crawlers.skims import SkimsCrawler
        return SkimsCrawler()

    if brand_id == "nanushka":
        from backend.crawlers.brand_crawlers.nanushka import NanushkaCrawler
        return NanushkaCrawler()

    if brand_id == "patagonia":
        from backend.crawlers.brand_crawlers.patagonia import PatagoniaCrawler
        return PatagoniaCrawler()

    if brand_id == "human_made":
        from backend.crawlers.brand_crawlers.human_made import HumanMadeCrawler
        return HumanMadeCrawler()

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
