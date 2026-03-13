"""TagWalk 런웨이 룩 크롤러.

tag-walk.com에서 디자이너별 컬렉션 룩 이미지를 수집한다.
robots.txt crawl-delay: 2초 준수.

Usage:
    python scripts/crawl_tagwalk.py
    python scripts/crawl_tagwalk.py --designers prada gucci
    python scripts/crawl_tagwalk.py --season fall-winter-2026
    python scripts/crawl_tagwalk.py --dry-run
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
from bs4 import BeautifulSoup

DB_PATH = Path(__file__).parent.parent / "backend" / "db" / "ftib.db"
BASE_URL = "https://www.tag-walk.com"

# 크롤링 대상 디자이너
DESIGNERS = {
    # ── 기존 (13개) ──
    "prada": {"name": "Prada", "slug": "prada"},
    "gucci": {"name": "Gucci", "slug": "gucci"},
    "lemaire": {"name": "Lemaire", "slug": "lemaire"},
    "dior": {"name": "Dior", "slug": "dior"},
    "saint-laurent": {"name": "Saint Laurent", "slug": "saint-laurent"},
    "balenciaga": {"name": "Balenciaga", "slug": "balenciaga"},
    "loewe": {"name": "Loewe", "slug": "loewe"},
    "celine": {"name": "Celine", "slug": "celine"},
    "miu-miu": {"name": "Miu Miu", "slug": "miu-miu"},
    "bottega-veneta": {"name": "Bottega Veneta", "slug": "bottega-veneta"},
    "valentino": {"name": "Valentino", "slug": "valentino"},
    "chanel": {"name": "Chanel", "slug": "chanel"},
    "hermes": {"name": "Hermes", "slug": "hermes"},
    # ── Tier 1: 메이저 럭셔리 (10개) ──
    "louis-vuitton": {"name": "Louis Vuitton", "slug": "louis-vuitton"},
    "fendi": {"name": "Fendi", "slug": "fendi"},
    "dolce-gabbana": {"name": "Dolce & Gabbana", "slug": "dolce-gabbana"},
    "givenchy": {"name": "Givenchy", "slug": "givenchy"},
    "burberry": {"name": "Burberry", "slug": "burberry"},
    "alexander-mcqueen": {"name": "Alexander McQueen", "slug": "alexander-mcqueen"},
    "versace": {"name": "Versace", "slug": "versace"},
    "balmain": {"name": "Balmain", "slug": "balmain"},
    "schiaparelli": {"name": "Schiaparelli", "slug": "schiaparelli"},
    "chloe": {"name": "Chloe", "slug": "chloe"},
    # ── Tier 2: 하이엔드 컨템포러리 (10개) ──
    "max-mara": {"name": "Max Mara", "slug": "max-mara"},
    "jil-sander": {"name": "Jil Sander", "slug": "jil-sander"},
    "acne-studios": {"name": "Acne Studios", "slug": "acne-studios"},
    "maison-margiela": {"name": "Maison Margiela", "slug": "maison-margiela"},
    "stella-mccartney": {"name": "Stella McCartney", "slug": "stella-mccartney"},
    "sacai": {"name": "Sacai", "slug": "sacai"},
    "rick-owens": {"name": "Rick Owens", "slug": "rick-owens"},
    "isabel-marant": {"name": "Isabel Marant", "slug": "isabel-marant"},
    "ferragamo": {"name": "Ferragamo", "slug": "ferragamo"},
    "marni": {"name": "Marni", "slug": "marni"},
    # ── Tier 3: 일본/한국 관심 (5개) ──
    "comme-des-garcons": {"name": "Comme des Garcons", "slug": "comme-des-garcons"},
    "issey-miyake": {"name": "Issey Miyake", "slug": "issey-miyake"},
    "junya-watanabe": {"name": "Junya Watanabe", "slug": "junya-watanabe"},
    "mame-kurogouchi": {"name": "Mame Kurogouchi", "slug": "mame-kurogouchi"},
    "thom-browne": {"name": "Thom Browne", "slug": "thom-browne"},
}

# 시즌 목록 (최신 순)
SEASONS = [
    "fall-winter-2026",
    "spring-summer-2026",
    "fall-winter-2025",
    "spring-summer-2025",
    "fall-winter-2024",
    "spring-summer-2024",
]

# 컬렉션 타입
COLLECTION_TYPES = ["woman", "man"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

CRAWL_DELAY = 2.5  # robots.txt says 2, add margin


def make_look_id(designer_slug: str, season: str, look_number: int, ctype: str) -> str:
    raw = f"tagwalk:{designer_slug}:{season}:{ctype}:{look_number}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def season_to_label(season: str) -> str:
    parts = season.replace("-", " ").title()
    return parts


def fetch_collection(designer_slug: str, season: str, ctype: str, city: str = "") -> list[dict]:
    """컬렉션 페이지를 가져와 룩 데이터를 파싱."""
    url = f"{BASE_URL}/en/collection/{ctype}/{designer_slug}/{season}"
    if city:
        url += f"?city={city}"

    print(f"  Fetching: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException as e:
        print(f"  Error fetching {url}: {e}")
        return []

    if resp.status_code == 302 or resp.status_code == 301:
        print(f"  Redirected (no collection found)")
        return []
    if resp.status_code != 200:
        print(f"  HTTP {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # 디자이너 메타데이터
    container = soup.find(attrs={"data-designer-name": True})
    designer_name = ""
    season_label = ""
    city_name = ""
    if container:
        designer_name = container.get("data-designer-name", designer_slug.title())
        season_label = container.get("data-season-name", season_to_label(season))
        city_name = container.get("data-city-name", city)

    looks = []

    # 룩 요소 찾기 — data-look 속성이 있는 요소
    look_elements = soup.find_all(attrs={"data-look": True})

    if not look_elements:
        # 대안: figure나 img 태그에서 cdn.tag-walk.com 이미지 찾기
        img_tags = soup.find_all("img", src=re.compile(r"cdn\.tag-walk\.com"))
        img_tags += soup.find_all("img", attrs={"data-src": re.compile(r"cdn\.tag-walk\.com")})

        for i, img in enumerate(img_tags, 1):
            src = img.get("data-src") or img.get("src") or ""
            if "cdn.tag-walk.com" not in src:
                continue

            # view 해상도로 변환
            view_url = re.sub(r"cdn\.tag-walk\.com/\w+/", "cdn.tag-walk.com/view/", src)
            thumb_url = re.sub(r"cdn\.tag-walk\.com/\w+/", "cdn.tag-walk.com/list/", src)

            looks.append({
                "id": make_look_id(designer_slug, season, i, ctype),
                "designer": designer_name or designer_slug.title(),
                "designer_slug": designer_slug,
                "season": season,
                "season_label": season_label or season_to_label(season),
                "city": city_name or city,
                "look_number": i,
                "image_url": view_url,
                "thumbnail_url": thumb_url,
                "source_url": url,
                "collection_type": ctype,
            })
    else:
        for el in look_elements:
            look_num = int(el.get("data-look", 0))

            # 이미지 찾기
            img = el.find("img")
            if not img:
                continue

            src = img.get("data-src") or img.get("src") or ""
            if not src:
                continue

            # CDN URL 정리
            if src.startswith("//"):
                src = "https:" + src
            if "cdn.tag-walk.com" not in src:
                continue

            view_url = re.sub(r"cdn\.tag-walk\.com/\w+/", "cdn.tag-walk.com/view/", src)
            thumb_url = re.sub(r"cdn\.tag-walk\.com/\w+/", "cdn.tag-walk.com/list/", src)

            looks.append({
                "id": make_look_id(designer_slug, season, look_num, ctype),
                "designer": designer_name or designer_slug.title(),
                "designer_slug": designer_slug,
                "season": season,
                "season_label": season_label or season_to_label(season),
                "city": city_name or city,
                "look_number": look_num,
                "image_url": view_url,
                "thumbnail_url": thumb_url,
                "source_url": url,
                "collection_type": ctype,
            })

    print(f"  Found {len(looks)} looks")
    return looks


def save_to_db(looks: list[dict]):
    """룩 데이터를 DB에 저장."""
    if not looks:
        return

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # 테이블 생성 (없을 경우)
    c.execute("""
        CREATE TABLE IF NOT EXISTS runway_looks (
            id              TEXT PRIMARY KEY,
            designer        TEXT NOT NULL,
            designer_slug   TEXT NOT NULL,
            season          TEXT NOT NULL,
            season_label    TEXT,
            city            TEXT,
            look_number     INTEGER,
            image_url       TEXT NOT NULL,
            thumbnail_url   TEXT,
            source_url      TEXT,
            collection_type TEXT DEFAULT 'woman',
            tags            TEXT,
            crawled_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    inserted = 0
    for look in looks:
        try:
            c.execute(
                """INSERT OR REPLACE INTO runway_looks
                   (id, designer, designer_slug, season, season_label, city,
                    look_number, image_url, thumbnail_url, source_url, collection_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    look["id"], look["designer"], look["designer_slug"],
                    look["season"], look["season_label"], look["city"],
                    look["look_number"], look["image_url"], look["thumbnail_url"],
                    look["source_url"], look["collection_type"],
                ),
            )
            inserted += 1
        except Exception as e:
            print(f"  DB error: {e}")

    conn.commit()
    conn.close()
    print(f"  Saved {inserted} looks to DB")


def main():
    parser = argparse.ArgumentParser(description="TagWalk runway crawler")
    parser.add_argument("--designers", nargs="+", default=list(DESIGNERS.keys()),
                        help="Designer slugs to crawl")
    parser.add_argument("--seasons", nargs="+", default=SEASONS[:2],
                        help="Seasons to crawl")
    parser.add_argument("--types", nargs="+", default=COLLECTION_TYPES[:1],
                        help="Collection types (woman/man)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    total_looks = []

    for designer_key in args.designers:
        designer = DESIGNERS.get(designer_key)
        if not designer:
            print(f"Unknown designer: {designer_key}")
            continue

        print(f"\n=== {designer['name']} ===")

        for season in args.seasons:
            for ctype in args.types:
                looks = fetch_collection(designer["slug"], season, ctype)
                total_looks.extend(looks)
                time.sleep(CRAWL_DELAY)

    print(f"\n--- Total: {len(total_looks)} looks ---")

    if args.dry_run:
        for look in total_looks[:5]:
            print(f"  [{look['designer']}] {look['season']} Look #{look['look_number']}: {look['image_url'][:80]}...")
    else:
        save_to_db(total_looks)


if __name__ == "__main__":
    main()
