"""TagWalk look/search 방식으로 런웨이 룩 재수집.

/en/collection/woman/{designer}/{season} URL이 302인 브랜드를 위해
/en/look/search?type=...&season=...&designer=...&city=paris 패턴으로 수집.

Usage:
    python scripts/recrawl_look_search.py
    python scripts/recrawl_look_search.py --dry-run
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DB_PATH = Path(__file__).parent.parent / "backend" / "db" / "ftib.db"
BASE_URL = "https://www.tag-walk.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

CRAWL_DELAY = 2.5

SEASONS = [
    "spring-summer-2026",
    "fall-winter-2026",
    "spring-summer-2025",
    "fall-winter-2025",
    "spring-summer-2024",
    "fall-winter-2024",
]

# 재수집 대상: (designer_slug, display_name, collection_type, seasons_to_crawl)
TARGETS = [
    # Lemaire: 여성 없음, 남성만 전 시즌
    ("lemaire", "Lemaire", "man", SEASONS),
    # Celine: SS2026만 재수집 (FW2026은 이미 정상)
    ("celine", "Celine", "woman", ["spring-summer-2026"]),
]

# 필터: 이 패턴이 포함된 URL은 제외
JUNK_PATTERNS = [
    "badge", "icon", "facebook", "instagram", "tik-tok",
    "linked-in", "app-store", "google-play", "twitter",
    "youtube", "pinterest", "snapchat",
]


def make_look_id(designer_slug: str, season: str, look_number: int, ctype: str) -> str:
    raw = f"tagwalk:{designer_slug}:{season}:{ctype}:{look_number}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def season_to_label(season: str) -> str:
    return season.replace("-", " ").title()


def is_junk_url(url: str) -> bool:
    url_lower = url.lower()
    return any(p in url_lower for p in JUNK_PATTERNS)


def fetch_look_search(designer_slug: str, season: str, ctype: str) -> list[dict]:
    """look/search 패턴으로 룩 수집."""
    url = (
        f"{BASE_URL}/en/look/search"
        f"?type={ctype}&season={season}&designer={designer_slug}&city=paris"
    )
    print(f"  Fetching: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
    except requests.RequestException as e:
        print(f"  Error: {e}")
        return []

    if resp.status_code != 200:
        print(f"  HTTP {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    looks = []

    # Strategy 1: data-look 속성이 있는 요소
    look_elements = soup.find_all(attrs={"data-look": True})

    if look_elements:
        for el in look_elements:
            look_num = int(el.get("data-look", 0))
            img = el.find("img")
            if not img:
                continue

            src = img.get("data-src") or img.get("src") or ""
            if not src:
                continue
            if src.startswith("//"):
                src = "https:" + src
            if "cdn.tag-walk.com" not in src:
                continue
            if is_junk_url(src):
                continue

            view_url = re.sub(r"cdn\.tag-walk\.com/\w+/", "cdn.tag-walk.com/view/", src)
            thumb_url = re.sub(r"cdn\.tag-walk\.com/\w+/", "cdn.tag-walk.com/list/", src)

            looks.append({
                "id": make_look_id(designer_slug, season, look_num, ctype),
                "designer_slug": designer_slug,
                "season": season,
                "season_label": season_to_label(season),
                "look_number": look_num,
                "image_url": view_url,
                "thumbnail_url": thumb_url,
                "source_url": url,
                "collection_type": ctype,
            })
    else:
        # Strategy 2: fallback — designer slug이 포함된 이미지만 수집
        img_tags = soup.find_all("img", src=re.compile(r"cdn\.tag-walk\.com"))
        img_tags += soup.find_all("img", attrs={"data-src": re.compile(r"cdn\.tag-walk\.com")})

        slug_lower = designer_slug.replace("-", "").lower()
        for i, img in enumerate(img_tags, 1):
            src = img.get("data-src") or img.get("src") or ""
            if "cdn.tag-walk.com" not in src:
                continue
            if is_junk_url(src):
                continue
            # Only keep images that contain the designer slug in filename
            filename = src.split("/")[-1].lower()
            if slug_lower not in filename:
                continue

            view_url = re.sub(r"cdn\.tag-walk\.com/\w+/", "cdn.tag-walk.com/view/", src)
            thumb_url = re.sub(r"cdn\.tag-walk\.com/\w+/", "cdn.tag-walk.com/list/", src)

            looks.append({
                "id": make_look_id(designer_slug, season, i, ctype),
                "designer_slug": designer_slug,
                "season": season,
                "season_label": season_to_label(season),
                "look_number": i,
                "image_url": view_url,
                "thumbnail_url": thumb_url,
                "source_url": url,
                "collection_type": ctype,
            })

    print(f"  Found {len(looks)} looks")
    return looks


def save_to_db(looks: list[dict], designer_name: str):
    if not looks:
        return

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    inserted = 0
    for look in looks:
        try:
            c.execute(
                """INSERT OR REPLACE INTO runway_looks
                   (id, designer, designer_slug, season, season_label, city,
                    look_number, image_url, thumbnail_url, source_url, collection_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    look["id"], designer_name, look["designer_slug"],
                    look["season"], look["season_label"], "paris",
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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for designer_slug, display_name, ctype, seasons in TARGETS:
        print(f"\n=== {display_name} ({ctype}) ===")
        for season in seasons:
            looks = fetch_look_search(designer_slug, season, ctype)

            if not args.dry_run and looks:
                save_to_db(looks, display_name)
            elif args.dry_run and looks:
                for look in looks[:3]:
                    print(f"    Look #{look['look_number']}: {look['image_url'][:80]}...")

            time.sleep(CRAWL_DELAY)

    # Summary
    if not args.dry_run:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute("""
            SELECT designer, season, collection_type, COUNT(*)
            FROM runway_looks
            WHERE designer IN ('Lemaire', 'Celine')
            GROUP BY designer, season, collection_type
            ORDER BY designer, season
        """)
        print("\n=== Final DB Status ===")
        for row in c.fetchall():
            print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} looks")
        conn.close()


if __name__ == "__main__":
    main()
