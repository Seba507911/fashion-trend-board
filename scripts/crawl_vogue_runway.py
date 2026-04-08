"""Vogue Runway 크롤러.

vogue.com/fashion-shows에서 런웨이 컬렉션 + 디테일 이미지를 수집한다.
window.__PRELOADED_STATE__ JSON에서 갤러리 데이터를 추출.

Usage:
    python scripts/crawl_vogue_runway.py
    python scripts/crawl_vogue_runway.py --designers prada gucci
    python scripts/crawl_vogue_runway.py --seasons spring-2026-ready-to-wear
    python scripts/crawl_vogue_runway.py --dry-run
    python scripts/crawl_vogue_runway.py --list-shows prada
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import time
from pathlib import Path

import requests

DB_PATH = Path(__file__).parent.parent / "backend" / "db" / "ftib.db"
BASE_URL = "https://www.vogue.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

CRAWL_DELAY = 2.0  # seconds between requests

# ──────────────────────────────────────────────
# 디자이너 목록 (TagWalk과 동일 + Vogue slug)
# ──────────────────────────────────────────────

DESIGNERS = {
    # Tier 1: 메이저 럭셔리
    "prada": {"name": "Prada", "city": "Milan"},
    "gucci": {"name": "Gucci", "city": "Milan"},
    "louis-vuitton": {"name": "Louis Vuitton", "city": "Paris"},
    "dior": {"name": "Dior", "city": "Paris"},
    "saint-laurent": {"name": "Saint Laurent", "city": "Paris"},
    "balenciaga": {"name": "Balenciaga", "city": "Paris"},
    "loewe": {"name": "Loewe", "city": "Paris"},
    "celine": {"name": "Celine", "city": "Paris"},
    "miu-miu": {"name": "Miu Miu", "city": "Milan"},
    "bottega-veneta": {"name": "Bottega Veneta", "city": "Milan"},
    "valentino": {"name": "Valentino", "city": "Milan"},
    "chanel": {"name": "Chanel", "city": "Paris"},
    "hermes": {"name": "Hermes", "city": "Paris"},
    "fendi": {"name": "Fendi", "city": "Milan"},
    "dolce-gabbana": {"name": "Dolce & Gabbana", "city": "Milan"},
    "givenchy": {"name": "Givenchy", "city": "Paris"},
    "burberry": {"name": "Burberry", "city": "London"},
    "alexander-mcqueen": {"name": "Alexander McQueen", "city": "Paris"},
    "versace": {"name": "Versace", "city": "Milan"},
    "balmain": {"name": "Balmain", "city": "Paris"},
    "schiaparelli": {"name": "Schiaparelli", "city": "Paris"},
    "chloe": {"name": "Chloe", "city": "Paris"},
    # Tier 2: 하이엔드 컨템포러리
    "max-mara": {"name": "Max Mara", "city": "Milan"},
    "jil-sander": {"name": "Jil Sander", "city": "Milan"},
    "acne-studios": {"name": "Acne Studios", "city": "Paris"},
    "maison-margiela": {"name": "Maison Margiela", "city": "Paris"},
    "stella-mccartney": {"name": "Stella McCartney", "city": "Paris"},
    "sacai": {"name": "Sacai", "city": "Paris"},
    "rick-owens": {"name": "Rick Owens", "city": "Paris"},
    "isabel-marant": {"name": "Isabel Marant", "city": "Paris"},
    "marni": {"name": "Marni", "city": "Milan"},
    # Tier 3: 일본/한국
    "comme-des-garcons": {"name": "Comme des Garcons", "city": "Paris"},
    "issey-miyake": {"name": "Issey Miyake", "city": "Paris"},
    "junya-watanabe": {"name": "Junya Watanabe", "city": "Paris"},
    "thom-browne": {"name": "Thom Browne", "city": "Paris"},
    "kenzo": {"name": "Kenzo", "city": "Paris"},
    "yohji-yamamoto": {"name": "Yohji Yamamoto", "city": "Paris"},
    # Tier 4: 떠오르는 / 영향력
    "coperni": {"name": "Coperni", "city": "Paris"},
    "off-white": {"name": "Off-White", "city": "Paris"},
    "marine-serre": {"name": "Marine Serre", "city": "Paris"},
    "jw-anderson": {"name": "JW Anderson", "city": "London"},
    "peter-do": {"name": "Peter Do", "city": "Paris"},
    "rokh": {"name": "Rokh", "city": "Paris"},
    "wales-bonner": {"name": "Wales Bonner", "city": "Paris"},
    # Tier 5: 한국/아시아
    "kimhekim": {"name": "Kimhekim", "city": "Paris"},
    "wooyoungmi": {"name": "Wooyoungmi", "city": "Paris"},
}

# ──────────────────────────────────────────────
# 시즌 매핑
# ──────────────────────────────────────────────

# Vogue 시즌 slug 목록 (크롤링 대상)
VOGUE_SEASONS = [
    # Ready-to-Wear (Women)
    "spring-2024-ready-to-wear", "fall-2024-ready-to-wear",
    "spring-2025-ready-to-wear", "fall-2025-ready-to-wear",
    "spring-2026-ready-to-wear", "fall-2026-ready-to-wear",
    # Menswear
    "spring-2024-menswear", "fall-2024-menswear",
    "spring-2025-menswear", "fall-2025-menswear",
    "spring-2026-menswear", "fall-2026-menswear",
]

# Vogue slug → FTIB 표준 시즌
SEASON_TO_FTIB = {
    "spring-2024-ready-to-wear": "spring-summer-2024",
    "fall-2024-ready-to-wear": "fall-winter-2024",
    "spring-2025-ready-to-wear": "spring-summer-2025",
    "fall-2025-ready-to-wear": "fall-winter-2025",
    "spring-2026-ready-to-wear": "spring-summer-2026",
    "fall-2026-ready-to-wear": "fall-winter-2026",
    "spring-2024-menswear": "spring-summer-2024",
    "fall-2024-menswear": "fall-winter-2024",
    "spring-2025-menswear": "spring-summer-2025",
    "fall-2025-menswear": "fall-winter-2025",
    "spring-2026-menswear": "spring-summer-2026",
    "fall-2026-menswear": "fall-winter-2026",
}

# Vogue slug → collection_type
SEASON_TO_TYPE = {s: ("rtw-man" if "menswear" in s else "rtw-woman") for s in VOGUE_SEASONS}


def _make_show_id(designer_slug: str, season_slug: str) -> str:
    return f"vogue:{designer_slug}:{season_slug}"


def _make_image_id(designer_slug: str, season_slug: str, image_type: str, number: int) -> str:
    raw = f"vogue:{designer_slug}:{season_slug}:{image_type}:{number}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _extract_preloaded_state(html: str) -> dict | None:
    """HTML에서 window.__PRELOADED_STATE__ JSON을 추출."""
    idx = html.find("window.__PRELOADED_STATE__")
    if idx < 0:
        return None

    start = html.find("=", idx) + 1
    depth = 0
    real_end = None
    for i, ch in enumerate(html[start:start + 10_000_000], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if depth == 0 and ch == "}":
            real_end = i + 1
            break

    if not real_end:
        return None

    try:
        return json.loads(html[start:real_end])
    except json.JSONDecodeError:
        return None


def _get_best_url(sources: dict, prefer: str = "lg") -> tuple[str, str, str]:
    """이미지 sources에서 (lg_url, md_url, sm_url) 반환."""
    lg = sources.get("xl", sources.get("lg", sources.get("md", {})))
    md = sources.get("md", sources.get("lg", {}))
    sm = sources.get("sm", {})
    return (
        lg.get("url", ""),
        md.get("url", ""),
        sm.get("url", ""),
    )


def _make_season_label(season_slug: str) -> str:
    """spring-2026-ready-to-wear → Spring 2026"""
    m = re.match(r"(spring|fall|resort|pre-fall)-(\d{4})", season_slug)
    if m:
        return f"{m.group(1).title()} {m.group(2)}"
    return season_slug.replace("-", " ").title()


# ──────────────────────────────────────────────
# 디자이너별 쇼 목록 가져오기
# ──────────────────────────────────────────────

def list_designer_shows(designer_slug: str) -> list[dict]:
    """디자이너 페이지에서 가용 시즌 목록을 가져온다."""
    url = f"{BASE_URL}/fashion-shows/designer/{designer_slug}"
    print(f"  Fetching designer page: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException as e:
        print(f"  Error: {e}")
        return []

    if resp.status_code != 200:
        print(f"  HTTP {resp.status_code}")
        return []

    data = _extract_preloaded_state(resp.text)
    if not data:
        print("  No __PRELOADED_STATE__")
        return []

    # 쇼 목록은 transformed.runwayDesignerContent 또는 유사 키에 있음
    t = data.get("transformed", {})
    shows = []

    # 방법 1: HTML에서 시즌 링크 추출 (더 안정적)
    season_links = re.findall(
        r'href="/fashion-shows/([^/"]+)/' + re.escape(designer_slug) + r'"',
        resp.text,
    )
    for season_slug in set(season_links):
        shows.append({
            "season_slug": season_slug,
            "designer_slug": designer_slug,
            "url": f"{BASE_URL}/fashion-shows/{season_slug}/{designer_slug}",
        })

    print(f"  Found {len(shows)} shows")
    return sorted(shows, key=lambda s: s["season_slug"])


# ──────────────────────────────────────────────
# 쇼 페이지에서 갤러리 데이터 추출
# ──────────────────────────────────────────────

def fetch_show_galleries(designer_slug: str, season_slug: str) -> dict | None:
    """쇼 페이지에서 메타데이터 + 갤러리 이미지를 추출."""
    url = f"{BASE_URL}/fashion-shows/{season_slug}/{designer_slug}"
    print(f"  Fetching show: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException as e:
        print(f"  Error: {e}")
        return None

    if resp.status_code != 200:
        print(f"  HTTP {resp.status_code}")
        return None

    data = _extract_preloaded_state(resp.text)
    if not data:
        print("  No __PRELOADED_STATE__")
        return None

    t = data.get("transformed", {})

    # ── 쇼 메타데이터 ──
    show_content = t.get("runwayShowContent", {})
    brand = show_content.get("brand", "")
    pub_date = show_content.get("pubDate", "")
    designers_dek = show_content.get("designersDek", "")

    header = show_content.get("sectionHeader", {})
    # show_name: "Prada Spring 2026 Ready-to-Wear" 형태
    show_name_raw = header.get("subHed", "")
    show_name_clean = re.sub(r"<[^>]+>", "", show_name_raw).strip()
    if brand and show_name_clean:
        show_name = f"{brand} {show_name_clean}"
    else:
        show_name = f"{brand} {_make_season_label(season_slug)}"

    designer_info = DESIGNERS.get(designer_slug, {})
    ftib_season = SEASON_TO_FTIB.get(season_slug, season_slug)
    collection_type = SEASON_TO_TYPE.get(season_slug, "rtw-woman")
    city = designer_info.get("city", "")

    # ── 갤러리 데이터 ──
    galleries_data = t.get("runwayShowGalleries", {})
    galleries = galleries_data.get("galleries", [])

    result = {
        "show": {
            "id": _make_show_id(designer_slug, season_slug),
            "designer": brand or designer_info.get("name", designer_slug),
            "designer_slug": designer_slug,
            "season_slug": season_slug,
            "season": ftib_season,
            "season_label": _make_season_label(season_slug),
            "show_name": show_name,
            "collection_type": collection_type,
            "city": city,
            "show_date": pub_date,
            "review_url": url,
        },
        "images": [],
    }

    # 갤러리별 이미지 추출
    for gallery in galleries:
        gallery_id = gallery.get("id", "")
        gallery_title = gallery.get("title", "")
        items = gallery.get("items", [])

        # gallery-collection → collection, gallery-detail → detail
        if "collection" in gallery_id.lower():
            image_type = "collection"
        elif "detail" in gallery_id.lower():
            image_type = "detail"
        elif "backstage" in gallery_id.lower():
            image_type = "backstage"
        elif "atmosphere" in gallery_id.lower():
            image_type = "atmosphere"
        elif "beauty" in gallery_id.lower():
            image_type = "beauty"
        else:
            image_type = gallery_title.lower().replace(" ", "_") or "other"

        for item in items:
            look_num_raw = item.get("lookNumber", "0")
            try:
                look_number = int(str(look_num_raw).lstrip("0") or "0")
            except ValueError:
                look_number = 0

            sources = item.get("image", {}).get("sources", {})
            lg_url, md_url, sm_url = _get_best_url(sources)

            if not lg_url:
                continue

            result["images"].append({
                "id": _make_image_id(designer_slug, season_slug, image_type, look_number or len(result["images"])),
                "show_id": result["show"]["id"],
                "designer": result["show"]["designer"],
                "designer_slug": designer_slug,
                "season": ftib_season,
                "image_type": image_type,
                "look_number": look_number,
                "image_url": lg_url,
                "image_url_md": md_url,
                "thumbnail_url": sm_url,
                "source_url": url,
                "alt_text": item.get("caption", ""),
            })

    # 통계
    collection_count = sum(1 for img in result["images"] if img["image_type"] == "collection")
    detail_count = sum(1 for img in result["images"] if img["image_type"] == "detail")
    other_count = len(result["images"]) - collection_count - detail_count
    result["show"]["total_looks"] = collection_count
    result["show"]["total_details"] = detail_count

    print(f"  {show_name}: {collection_count} collection + {detail_count} detail + {other_count} other = {len(result['images'])} total")
    return result


# ──────────────────────────────────────────────
# DB 저장
# ──────────────────────────────────────────────

def save_to_db(result: dict):
    """쇼 + 이미지를 DB에 저장."""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    show = result["show"]

    c.execute(
        """INSERT OR REPLACE INTO vogue_shows
           (id, designer, designer_slug, season_slug, season, season_label,
            show_name, collection_type, city, show_date, review_url,
            total_looks, total_details)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            show["id"], show["designer"], show["designer_slug"],
            show["season_slug"], show["season"], show["season_label"],
            show["show_name"], show["collection_type"], show["city"],
            show["show_date"], show["review_url"],
            show["total_looks"], show["total_details"],
        ),
    )

    for img in result["images"]:
        c.execute(
            """INSERT OR REPLACE INTO vogue_runway_images
               (id, show_id, designer, designer_slug, season,
                image_type, look_number, image_url, image_url_md,
                thumbnail_url, source_url, alt_text)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                img["id"], img["show_id"], img["designer"],
                img["designer_slug"], img["season"],
                img["image_type"], img["look_number"],
                img["image_url"], img["image_url_md"],
                img["thumbnail_url"], img["source_url"],
                img["alt_text"],
            ),
        )

    conn.commit()
    conn.close()
    print(f"  Saved {len(result['images'])} images to DB")


# ──────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Vogue Runway 크롤러")
    parser.add_argument("--designers", nargs="+", help="디자이너 slug 목록")
    parser.add_argument("--seasons", nargs="+", help="Vogue 시즌 slug 목록")
    parser.add_argument("--dry-run", action="store_true", help="DB 저장 없이 미리보기")
    parser.add_argument("--list-shows", metavar="DESIGNER", help="디자이너의 가용 쇼 목록 출력")
    args = parser.parse_args()

    # 쇼 목록 조회 모드
    if args.list_shows:
        shows = list_designer_shows(args.list_shows)
        for s in shows:
            print(f"  {s['season_slug']}")
        return

    # 대상 디자이너
    designer_slugs = args.designers or list(DESIGNERS.keys())

    # 대상 시즌
    target_seasons = args.seasons or VOGUE_SEASONS

    total_shows = 0
    total_images = 0

    for slug in designer_slugs:
        if slug not in DESIGNERS:
            print(f"Unknown designer: {slug}")
            continue

        print(f"\n{'='*60}")
        print(f"=== {DESIGNERS[slug]['name']} ===")
        print(f"{'='*60}")

        for season_slug in target_seasons:
            result = fetch_show_galleries(slug, season_slug)

            if result and result["images"]:
                total_shows += 1
                total_images += len(result["images"])

                if args.dry_run:
                    for img in result["images"][:3]:
                        print(f"    [{img['image_type']}] #{img['look_number']} {img['image_url'][:80]}...")
                    if len(result["images"]) > 3:
                        print(f"    ... +{len(result['images']) - 3} more")
                else:
                    save_to_db(result)

            time.sleep(CRAWL_DELAY)

    print(f"\n{'='*60}")
    print(f"DONE: {total_shows} shows, {total_images} images")
    print(f"{'='*60}")

    # DB 요약
    if not args.dry_run and total_images > 0:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM vogue_shows")
        show_count = c.fetchone()[0]
        c.execute("SELECT image_type, COUNT(*) FROM vogue_runway_images GROUP BY image_type")
        type_counts = {r[0]: r[1] for r in c.fetchall()}
        conn.close()
        print(f"\nDB Status: {show_count} shows")
        for t, cnt in sorted(type_counts.items()):
            print(f"  {t}: {cnt} images")


if __name__ == "__main__":
    main()
