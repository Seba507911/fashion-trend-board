"""무신사 파일럿 크롤러 — 브랜드별 상품 상세 수집."""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "backend" / "db" / "ftib.db"

PILOT_BRANDS = [
    {"slug": "musinsastandard", "name": "무신사 스탠다드", "zoning": "SPA/매스"},
    {"slug": "anderssonbell", "name": "앤더슨벨", "zoning": "컨템포러리"},
    {"slug": "partimento", "name": "파르티멘토", "zoning": "캐주얼"},
    {"slug": "letterfrommoon", "name": "레터프롬문", "zoning": "여성 캐주얼"},
    {"slug": "placestudio", "name": "플레이스스튜디오", "zoning": "여성 캐주얼"},
]

EXTRACT_DETAIL_JS = """() => {
    const result = {};

    // 1. JSON-LD
    const ldScript = document.querySelector('script[type="application/ld+json"]');
    if (ldScript) {
        try { result.ld = JSON.parse(ldScript.textContent); } catch {}
    }

    // 2. Meta tags
    const metas = {};
    document.querySelectorAll('meta[property]').forEach(m => {
        const p = m.getAttribute('property');
        if (p) metas[p] = m.content;
    });
    result.meta = metas;

    // 3. Page text parsing for structured fields
    const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l);
    const info = {};
    const keys = ['품번','시즌','성별','조회수','누적판매','좋아요','색상','소재','혼용률','겉감','안감','제조국'];
    for (let i = 0; i < lines.length; i++) {
        for (const key of keys) {
            if (lines[i] === key && i + 1 < lines.length && lines[i+1].length < 100) {
                info[key] = lines[i + 1];
            }
        }
    }
    result.info = info;

    // 4. Detail images (product shots, not UI)
    const imgs = Array.from(document.querySelectorAll('img'))
        .map(i => i.src || '')
        .filter(s => s.includes('msscdn.net/images/') || s.includes('msscdn.net/thumbnails/'));
    // Get high-res versions
    const hiRes = imgs.map(u => u.replace('/thumbnails/', '/').replace(/_\\d+\\./, '_500.'));
    result.detailImages = [...new Set(hiRes)].slice(0, 8);

    // 5. Color from product name or options
    const title = document.title || '';
    const colorMatch = title.match(/\\[([^\\]]+)\\]/);
    result.color = colorMatch ? colorMatch[1] : '';

    return result;
}"""


def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS musinsa_products (
            id TEXT PRIMARY KEY,
            brand_slug TEXT NOT NULL,
            brand_name TEXT NOT NULL,
            product_code TEXT,
            product_name TEXT NOT NULL,
            price INTEGER,
            sale_price INTEGER,
            original_price INTEGER,
            sale_rate TEXT,
            currency TEXT DEFAULT 'KRW',
            category TEXT,
            image_url TEXT,
            detail_images TEXT,
            product_url TEXT,
            rating REAL,
            review_count INTEGER,
            season TEXT,
            gender TEXT,
            color TEXT,
            description TEXT,
            view_count TEXT,
            like_count TEXT,
            sell_count TEXT,
            product_info TEXT,
            crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_musinsa_brand ON musinsa_products(brand_slug);
        CREATE INDEX IF NOT EXISTS idx_musinsa_name ON musinsa_products(product_name);
    """)
    conn.close()


async def crawl_brand(page, brand: dict, max_scroll: int = 15) -> list[dict]:
    url = f"https://www.musinsa.com/brand/{brand['slug']}/products"
    print(f"\n  Crawling: {brand['name']} ({url})")

    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(3)

    # Scroll to load products
    for _ in range(max_scroll):
        prev = await page.evaluate("document.body.scrollHeight")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.5)
        curr = await page.evaluate("document.body.scrollHeight")
        if curr == prev:
            break

    product_urls = await page.evaluate("""() => {
        const links = Array.from(document.querySelectorAll('a[href*="/products/"]'));
        return [...new Set(links.map(a => a.href).filter(h => /\\/products\\/\\d+/.test(h)))];
    }""")

    print(f"  Found {len(product_urls)} product URLs")
    products = []

    for i, purl in enumerate(product_urls[:40]):
        try:
            await page.goto(purl, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2.5)

            data = await page.evaluate(EXTRACT_DETAIL_JS)

            ld = data.get("ld", {})
            meta = data.get("meta", {})
            info = data.get("info", {})

            name = ld.get("name", "")
            if not name:
                continue

            agg = ld.get("aggregateRating", {})
            offers = ld.get("offers", {})
            brand_name = ld.get("brand", {}).get("name", "") or brand["name"]

            pid = hashlib.md5(f"musinsa:{brand['slug']}:{purl}".encode()).hexdigest()[:16]

            products.append({
                "id": pid,
                "brand_slug": brand["slug"],
                "brand_name": brand_name,
                "product_code": info.get("품번", ""),
                "product_name": name,
                "price": offers.get("price", 0),
                "original_price": int(meta.get("product:price:normal_price", 0) or 0),
                "sale_rate": meta.get("product:price:sale_rate", ""),
                "image_url": ld.get("image", ""),
                "detail_images": json.dumps(data.get("detailImages", []), ensure_ascii=False),
                "product_url": purl,
                "rating": agg.get("ratingValue"),
                "review_count": agg.get("reviewCount"),
                "season": info.get("시즌", ""),
                "gender": info.get("성별", ""),
                "color": data.get("color", ""),
                "description": meta.get("og:description", "")[:300],
                "view_count": info.get("조회수", ""),
                "sell_count": info.get("누적판매", ""),
                "like_count": info.get("좋아요", ""),
            })

            if (i + 1) % 10 == 0:
                print(f"    {i+1}/{min(len(product_urls), 40)} products...")

        except Exception as e:
            print(f"    Error: {purl[-20:]} — {str(e)[:50]}")

    print(f"  Collected: {len(products)} products")
    return products


def save_products(products: list[dict]):
    if not products:
        return
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    for p in products:
        c.execute("""
            INSERT OR REPLACE INTO musinsa_products
            (id, brand_slug, brand_name, product_code, product_name, price,
             original_price, sale_rate, image_url, detail_images, product_url,
             rating, review_count, season, gender, color, description,
             view_count, sell_count, like_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["id"], p["brand_slug"], p["brand_name"], p["product_code"],
            p["product_name"], p["price"], p["original_price"], p["sale_rate"],
            p["image_url"], p["detail_images"], p["product_url"],
            p["rating"], p["review_count"], p["season"], p["gender"],
            p["color"], p["description"], p["view_count"], p["sell_count"],
            p["like_count"],
        ))
    conn.commit()
    conn.close()
    print(f"  Saved {len(products)} to DB")


async def main():
    from playwright.async_api import async_playwright
    from playwright_stealth import Stealth

    init_db()

    stealth = Stealth()
    async with async_playwright() as pw:
        stealth.hook_playwright_context(pw)
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900}, locale="ko-KR"
        )
        page = await ctx.new_page()

        total = 0
        for brand in PILOT_BRANDS:
            products = await crawl_brand(page, brand)
            save_products(products)
            total += len(products)

        await browser.close()

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("SELECT brand_name, COUNT(*), COUNT(NULLIF(season,'')) as with_season FROM musinsa_products GROUP BY brand_name")
    print(f"\n{'='*50}")
    print(f"DONE: {total} products total")
    for r in c.fetchall():
        print(f"  {r[0]}: {r[1]} products ({r[2]} with season)")
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
