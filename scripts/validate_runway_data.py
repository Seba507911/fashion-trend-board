"""런웨이 데이터 교차 검증 스크립트.

DB의 runway_looks 데이터를 검증하고, 문제 있는 항목을 리포트한다.

검증 항목:
1. 26개 패턴 감지 (홈페이지 junk 수집 의심)
2. junk URL 감지 (badge, icon, SNS 아이콘)
3. 이미지 파일명에 designer slug 미포함 (다른 브랜드 이미지 혼입)
4. designer 이름 불일치 감지 (같은 slug인데 다른 display name)
5. TagWalk 실제 가용성 검증 (HTTP 요청)

Usage:
    python scripts/validate_runway_data.py                # 로컬 DB만 검증
    python scripts/validate_runway_data.py --check-remote  # TagWalk 실제 접속 확인
    python scripts/validate_runway_data.py --fix           # 문제 데이터 삭제
    python scripts/validate_runway_data.py --fix --check-remote  # 삭제 + 재수집 시도
"""
from __future__ import annotations

import argparse
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

JUNK_PATTERNS = [
    "badge", "icon", "facebook", "instagram", "tik-tok",
    "linked-in", "app-store", "google-play", "twitter",
    "youtube", "pinterest", "snapchat",
]

# TagWalk slug → 실제 slug 매핑 (알려진 불일치)
SLUG_CORRECTIONS = {
    "dior": "christian-dior",
    # 필요 시 추가
}


def is_junk_url(url: str) -> bool:
    url_lower = url.lower()
    return any(p in url_lower for p in JUNK_PATTERNS)


def get_filename_from_url(url: str) -> str:
    return url.split("/")[-1].lower()


def check_slug_in_filename(designer_slug: str, filename: str) -> bool:
    """파일명에 디자이너 slug가 포함되어 있는지 확인."""
    slug_clean = designer_slug.replace("-", "").lower()
    filename_clean = filename.lower()
    return slug_clean in filename_clean


def validate_local(conn: sqlite3.Connection) -> dict:
    """로컬 DB 검증."""
    c = conn.cursor()

    results = {
        "count_26_suspects": [],
        "junk_urls": [],
        "slug_mismatch": [],
        "name_duplicates": [],
        "summary": {},
    }

    # 1. 26개 패턴 감지
    c.execute("""
        SELECT designer, designer_slug, season, collection_type, COUNT(*) as cnt
        FROM runway_looks
        GROUP BY designer, designer_slug, season, collection_type
        HAVING cnt = 26
        ORDER BY designer, season
    """)
    results["count_26_suspects"] = [
        {"designer": r[0], "slug": r[1], "season": r[2], "ctype": r[3], "count": r[4]}
        for r in c.fetchall()
    ]

    # 2. junk URL 감지
    c.execute("SELECT id, designer, season, look_number, image_url FROM runway_looks")
    for row in c.fetchall():
        look_id, designer, season, look_num, url = row
        if is_junk_url(url):
            results["junk_urls"].append({
                "id": look_id, "designer": designer, "season": season,
                "look_number": look_num, "image_url": url,
            })

    # 3. 이미지 파일명에 designer slug 미포함
    c.execute("""
        SELECT id, designer, designer_slug, season, look_number, image_url
        FROM runway_looks
        WHERE designer_slug IS NOT NULL
    """)
    for row in c.fetchall():
        look_id, designer, slug, season, look_num, url = row
        filename = get_filename_from_url(url)
        if not check_slug_in_filename(slug, filename) and not is_junk_url(url):
            results["slug_mismatch"].append({
                "id": look_id, "designer": designer, "slug": slug,
                "season": season, "look_number": look_num,
                "filename": filename,
            })

    # 4. 같은 slug인데 다른 display name
    c.execute("""
        SELECT designer_slug, GROUP_CONCAT(DISTINCT designer) as names,
               COUNT(DISTINCT designer) as name_count
        FROM runway_looks
        WHERE designer_slug IS NOT NULL
        GROUP BY designer_slug
        HAVING name_count > 1
    """)
    results["name_duplicates"] = [
        {"slug": r[0], "names": r[1], "count": r[2]}
        for r in c.fetchall()
    ]

    # Summary
    c.execute("SELECT COUNT(*) FROM runway_looks")
    total = c.fetchone()[0]
    junk_count = len(results["junk_urls"])
    suspect_count = sum(r["count"] for r in results["count_26_suspects"])

    results["summary"] = {
        "total_looks": total,
        "count_26_suspect_entries": len(results["count_26_suspects"]),
        "count_26_suspect_looks": suspect_count,
        "junk_url_count": junk_count,
        "slug_mismatch_count": len(results["slug_mismatch"]),
        "name_duplicate_slugs": len(results["name_duplicates"]),
    }

    return results


def check_remote_availability(slug: str, season: str, ctype: str = "woman") -> dict:
    """TagWalk에서 실제 컬렉션 가용성 확인."""
    # 1차: direct collection URL
    direct_url = f"{BASE_URL}/en/collection/{ctype}/{slug}/{season}"
    try:
        resp = requests.get(direct_url, headers=HEADERS, timeout=15, allow_redirects=False)
    except requests.RequestException:
        return {"url_type": "direct", "status": "error", "looks": 0}

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        title = (soup.find("title").string or "").strip().lower() if soup.find("title") else ""
        if "discover" in title or "search engine" in title:
            direct_ok = False
        else:
            look_els = soup.find_all(attrs={"data-look": True})
            if look_els:
                return {"url_type": "direct", "status": "ok", "looks": len(look_els)}
            direct_ok = False
    else:
        direct_ok = False

    # 2차: look/search URL
    search_url = (
        f"{BASE_URL}/en/look/search"
        f"?type={ctype}&season={season}&designer={slug}&city=paris"
    )
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=15, allow_redirects=True)
    except requests.RequestException:
        return {"url_type": "search", "status": "error", "looks": 0}

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        look_els = soup.find_all(attrs={"data-look": True})
        if look_els:
            return {"url_type": "search", "status": "ok", "looks": len(look_els)}

    # 3차: 알려진 slug 교정 시도
    corrected = SLUG_CORRECTIONS.get(slug)
    if corrected:
        corrected_url = f"{BASE_URL}/en/collection/{ctype}/{corrected}/{season}"
        try:
            resp = requests.get(corrected_url, headers=HEADERS, timeout=15, allow_redirects=False)
        except requests.RequestException:
            return {"url_type": "corrected", "status": "error", "looks": 0}

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            title = (soup.find("title").string or "").strip().lower() if soup.find("title") else ""
            if "discover" not in title and "search engine" not in title:
                look_els = soup.find_all(attrs={"data-look": True})
                if look_els:
                    return {
                        "url_type": "corrected",
                        "status": "ok",
                        "looks": len(look_els),
                        "corrected_slug": corrected,
                    }

    return {"url_type": "none", "status": "not_found", "looks": 0}


def fix_junk_data(conn: sqlite3.Connection, results: dict, check_remote: bool = False):
    """문제 데이터 삭제."""
    c = conn.cursor()

    # 1. junk URL 삭제
    if results["junk_urls"]:
        junk_ids = [r["id"] for r in results["junk_urls"]]
        placeholders = ",".join("?" * len(junk_ids))
        c.execute(f"DELETE FROM runway_looks WHERE id IN ({placeholders})", junk_ids)
        print(f"  Deleted {c.rowcount} junk URL records")

    # 2. 26개 패턴 중 전체가 slug mismatch인 항목 삭제
    for suspect in results["count_26_suspects"]:
        designer = suspect["designer"]
        season = suspect["season"]

        # 해당 항목의 이미지 URL 검사
        c.execute(
            "SELECT id, image_url FROM runway_looks WHERE designer=? AND season=?",
            (designer, season),
        )
        rows = c.fetchall()
        slug = suspect["slug"]
        slug_clean = slug.replace("-", "").lower() if slug else ""

        junk_count = sum(1 for _, url in rows if is_junk_url(url))
        mismatch_count = sum(
            1 for _, url in rows
            if not is_junk_url(url) and slug_clean and slug_clean not in get_filename_from_url(url)
        )

        # 전부 junk이거나 대부분 mismatch면 삭제
        if junk_count + mismatch_count >= len(rows) * 0.8:
            ids = [r[0] for r in rows]
            placeholders = ",".join("?" * len(ids))
            c.execute(f"DELETE FROM runway_looks WHERE id IN ({placeholders})", ids)
            print(f"  Deleted {c.rowcount} suspect records: {designer} {season}")

    # 3. 고아 VLM 라벨 삭제
    c.execute("""
        DELETE FROM vlm_labels
        WHERE source_type='runway'
          AND source_id NOT IN (SELECT id FROM runway_looks)
    """)
    if c.rowcount:
        print(f"  Deleted {c.rowcount} orphaned VLM labels")

    conn.commit()


def make_look_id(designer_slug: str, season: str, look_number: int, ctype: str) -> str:
    raw = f"tagwalk:{designer_slug}:{season}:{ctype}:{look_number}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def recrawl_via_search(
    conn: sqlite3.Connection, slug: str, designer_name: str,
    season: str, ctype: str,
) -> int:
    """look/search URL로 재수집."""
    url = (
        f"{BASE_URL}/en/look/search"
        f"?type={ctype}&season={season}&designer={slug}&city=paris"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
    except requests.RequestException:
        return 0

    if resp.status_code != 200:
        return 0

    soup = BeautifulSoup(resp.text, "html.parser")
    look_elements = soup.find_all(attrs={"data-look": True})
    if not look_elements:
        return 0

    c = conn.cursor()
    inserted = 0
    for el in look_elements:
        look_num = int(el.get("data-look", 0))
        img = el.find("img")
        if not img:
            continue
        src = img.get("data-src") or img.get("src") or ""
        if not src or "cdn.tag-walk.com" not in src:
            continue
        if is_junk_url(src):
            continue
        if src.startswith("//"):
            src = "https:" + src

        view_url = re.sub(r"cdn\.tag-walk\.com/\w+/", "cdn.tag-walk.com/view/", src)
        thumb_url = re.sub(r"cdn\.tag-walk\.com/\w+/", "cdn.tag-walk.com/list/", src)
        look_id = make_look_id(slug, season, look_num, ctype)

        season_label = season.replace("-", " ").title()
        try:
            c.execute(
                """INSERT OR REPLACE INTO runway_looks
                   (id, designer, designer_slug, season, season_label, city,
                    look_number, image_url, thumbnail_url, source_url, collection_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (look_id, designer_name, slug, season, season_label, "paris",
                 look_num, view_url, thumb_url, url, ctype),
            )
            inserted += 1
        except Exception:
            pass

    conn.commit()
    return inserted


def print_report(results: dict):
    """검증 결과 리포트 출력."""
    s = results["summary"]
    print("\n" + "=" * 70)
    print("  RUNWAY DATA VALIDATION REPORT")
    print("=" * 70)

    print(f"\n  Total looks in DB: {s['total_looks']}")
    print(f"  26-count suspect entries: {s['count_26_suspect_entries']} "
          f"({s['count_26_suspect_looks']} looks)")
    print(f"  Junk URL records: {s['junk_url_count']}")
    print(f"  Slug mismatch records: {s['slug_mismatch_count']}")
    print(f"  Name duplicate slugs: {s['name_duplicate_slugs']}")

    if results["count_26_suspects"]:
        print(f"\n--- 26-COUNT SUSPECTS (likely homepage scrape) ---")
        for r in results["count_26_suspects"]:
            print(f"  {r['designer']:25s} | {r['season']:22s} | {r['ctype']} | {r['count']}")

    if results["name_duplicates"]:
        print(f"\n--- NAME DUPLICATES (same slug, different display name) ---")
        for r in results["name_duplicates"]:
            print(f"  slug: {r['slug']:25s} → names: {r['names']}")

    if results["slug_mismatch"][:10]:
        print(f"\n--- SLUG MISMATCH SAMPLES (first 10) ---")
        for r in results["slug_mismatch"][:10]:
            print(f"  {r['designer']:20s} | {r['season']:22s} | "
                  f"slug={r['slug']} | file={r['filename'][:50]}")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Runway data validator")
    parser.add_argument("--check-remote", action="store_true",
                        help="TagWalk 실제 접속 확인")
    parser.add_argument("--fix", action="store_true",
                        help="문제 데이터 삭제")
    parser.add_argument("--recrawl", action="store_true",
                        help="삭제 후 look/search로 재수집 시도")
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))

    print("Validating local DB...")
    results = validate_local(conn)
    print_report(results)

    if args.check_remote and results["count_26_suspects"]:
        print("\n--- REMOTE AVAILABILITY CHECK ---")
        checked = set()
        for suspect in results["count_26_suspects"]:
            slug = suspect["slug"]
            season = suspect["season"]
            key = (slug, season)
            if key in checked:
                continue
            checked.add(key)

            avail = check_remote_availability(slug, season)
            status_str = (
                f"  {suspect['designer']:25s} | {season:22s} | "
                f"remote: {avail['status']:10s} | {avail['looks']} looks | via {avail['url_type']}"
            )
            if avail.get("corrected_slug"):
                status_str += f" (corrected: {avail['corrected_slug']})"
            print(status_str)
            time.sleep(CRAWL_DELAY)

    if args.fix:
        print("\n--- FIXING DATA ---")
        fix_junk_data(conn, results, args.check_remote)

        # Re-validate
        results_after = validate_local(conn)
        print(f"\n  After fix: {results_after['summary']['total_looks']} total looks "
              f"({results_after['summary']['count_26_suspect_entries']} suspects remaining)")

    if args.recrawl:
        print("\n--- RECRAWL VIA LOOK/SEARCH ---")
        # Re-check suspects that were deleted
        conn2 = sqlite3.connect(str(DB_PATH))
        c = conn2.cursor()
        for suspect in results["count_26_suspects"]:
            slug = suspect["slug"]
            season = suspect["season"]
            designer = suspect["designer"]
            ctype = suspect["ctype"]

            # Check if still in DB (not deleted)
            c.execute(
                "SELECT COUNT(*) FROM runway_looks WHERE designer_slug=? AND season=?",
                (slug, season),
            )
            if c.fetchone()[0] > 0:
                continue

            print(f"  Trying recrawl: {designer} {season}...")
            count = recrawl_via_search(conn2, slug, designer, season, ctype)
            if count:
                print(f"    → Recrawled {count} looks")
            else:
                print(f"    → No data found on TagWalk")
            time.sleep(CRAWL_DELAY)

        conn2.close()

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
