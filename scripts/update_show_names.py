"""기존 runway_looks의 show_name, season_shortname을 TagWalk에서 가져와 업데이트.

각 (designer_slug, season, collection_type) 조합에 대해 TagWalk 페이지에서
실제 메타데이터를 읽어 show_name을 구성한다.

show_name 형식: "{Designer} {Season} {Year} {CollectionType}"
예: "Prada Spring 2026 Ready-to-Wear", "Lemaire Spring 2026 Menswear"

Usage:
    python scripts/update_show_names.py           # 전체 업데이트
    python scripts/update_show_names.py --dry-run  # 미리보기만
"""
from __future__ import annotations

import argparse
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

# collection_type → 표준 명칭
COLLECTION_TYPE_LABELS = {
    "woman": "Ready-to-Wear",
    "man": "Menswear",
    "couture": "Haute Couture",
    "resort": "Resort",
    "pre-fall": "Pre-Fall",
    "accessory": "Accessories",
}

# season slug → (계절, 연도)
SEASON_PARTS = {
    "spring-summer-2024": ("Spring", "2024"),
    "fall-winter-2024": ("Fall", "2024"),
    "spring-summer-2025": ("Spring", "2025"),
    "fall-winter-2025": ("Fall", "2025"),
    "spring-summer-2026": ("Spring", "2026"),
    "fall-winter-2026": ("Fall", "2026"),
}

SEASON_SHORTNAMES = {
    "spring-summer-2024": "SS24",
    "fall-winter-2024": "FW24",
    "spring-summer-2025": "SS25",
    "fall-winter-2025": "FW25",
    "spring-summer-2026": "SS26",
    "fall-winter-2026": "FW26",
}


def build_show_name(
    designer_name: str,
    season: str,
    collection_type: str,
    remote_season_name: str | None = None,
) -> str:
    """표준 쇼 명칭 구성."""
    # 계절+연도
    parts = SEASON_PARTS.get(season)
    if parts:
        season_str, year = parts
    elif remote_season_name:
        # "Spring/Summer 2026" → "Spring", "2026"
        clean = remote_season_name.replace("/", " ").split()
        season_str = clean[0] if clean else "Unknown"
        year = clean[-1] if clean else ""
    else:
        season_str = season.replace("-", " ").title()
        year = ""

    # 컬렉션 타입
    ctype_label = COLLECTION_TYPE_LABELS.get(collection_type, collection_type.title())

    return f"{designer_name} {season_str} {year} {ctype_label}".strip()


def fetch_remote_metadata(slug: str, season: str, ctype: str) -> dict | None:
    """TagWalk에서 실제 메타데이터 가져오기."""
    # 1차: direct collection URL
    url = f"{BASE_URL}/en/collection/{ctype}/{slug}/{season}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=False)
    except requests.RequestException:
        resp = None

    if resp and resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        el = soup.find(attrs={"data-look": True})
        if el:
            return {
                "designer_name": el.get("data-designer-name", ""),
                "season_name": el.get("data-season-name", ""),
                "season_shortname": el.get("data-season-shortname", ""),
                "city": el.get("data-city-name", ""),
                "type": el.get("data-type", ctype),
            }

    # 2차: look/search URL
    search_url = (
        f"{BASE_URL}/en/look/search"
        f"?type={ctype}&season={season}&designer={slug}&city=paris"
    )
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=15, allow_redirects=True)
    except requests.RequestException:
        return None

    if resp and resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        el = soup.find(attrs={"data-look": True})
        if el:
            return {
                "designer_name": el.get("data-designer-name", ""),
                "season_name": el.get("data-season-name", ""),
                "season_shortname": el.get("data-season-shortname", ""),
                "city": el.get("data-city-name", ""),
                "type": el.get("data-type", ctype),
            }

    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--remote", action="store_true",
                        help="TagWalk에서 실제 메타데이터 가져오기 (느림)")
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # 고유 (designer, designer_slug, season, collection_type) 조합
    c.execute("""
        SELECT DISTINCT designer, designer_slug, season, collection_type
        FROM runway_looks
        ORDER BY designer, season
    """)
    combos = c.fetchall()
    print(f"Found {len(combos)} unique designer-season-type combinations\n")

    updated = 0
    for designer, slug, season, ctype in combos:
        shortname = SEASON_SHORTNAMES.get(season, "")
        remote_meta = None

        if args.remote:
            remote_meta = fetch_remote_metadata(slug, season, ctype)
            time.sleep(CRAWL_DELAY)

        # show_name 구성
        if remote_meta and remote_meta["designer_name"]:
            show_name = build_show_name(
                remote_meta["designer_name"],
                season,
                remote_meta.get("type", ctype),
                remote_meta.get("season_name"),
            )
            shortname = remote_meta.get("season_shortname", shortname)
            # designer name도 교정 (TagWalk 공식명)
            real_designer = remote_meta["designer_name"]
        else:
            show_name = build_show_name(designer, season, ctype)
            real_designer = designer

        if args.dry_run:
            print(f"  {designer:25s} | {season:22s} | {ctype:6s} → {show_name} [{shortname}]")
            if remote_meta and real_designer != designer:
                print(f"    ↳ name fix: {designer} → {real_designer}")
        else:
            c.execute("""
                UPDATE runway_looks
                SET show_name = ?, season_shortname = ?, season_label = ?,
                    designer = ?
                WHERE designer_slug = ? AND season = ? AND collection_type = ?
            """, (
                show_name, shortname,
                remote_meta["season_name"] if remote_meta else season.replace("-", " ").title(),
                real_designer,
                slug, season, ctype,
            ))
            updated += c.rowcount
            print(f"  Updated {c.rowcount:4d} rows: {show_name} [{shortname}]")

    if not args.dry_run:
        conn.commit()
        print(f"\nTotal updated: {updated} rows")

    # Show results
    c.execute("""
        SELECT DISTINCT designer, show_name, season_shortname, collection_type
        FROM runway_looks
        ORDER BY designer, season_shortname
    """)
    print(f"\n{'='*80}")
    print(f"  SHOW NAME CATALOG")
    print(f"{'='*80}")
    for row in c.fetchall():
        print(f"  {row[0]:25s} | {row[1] or '(none)':50s} | {row[2] or '':5s} | {row[3]}")

    conn.close()


if __name__ == "__main__":
    main()
