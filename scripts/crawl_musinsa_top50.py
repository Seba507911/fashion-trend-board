"""무신사 Top 50 브랜드 일괄 크롤러 — 컬러 그루핑 포함."""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "backend" / "db" / "ftib.db"

TOP50_BRANDS = [
    "thenorthface", "musinsastandard", "lululemon", "musinsastandardwoman",
    "snowpeakapparel", "adidas", "malbongolf", "descente",
    "discoveryexpedition", "newbalance", "xexymix", "kodak",
    "nationalgeographic", "nike", "k2", "kolonsport", "hadex",
    "blackyak", "eider", "universalchemistry", "dynafit", "diadora",
    "borntowin", "adidasgolf", "dod1", "sierradesigns", "anewgolf",
    "musinsastandardsp", "puma", "8seconds", "sergiotacchini", "columbia",
    "nordisk", "descentegolf", "nepa", "wideangle", "montbell", "spao",
    "mixxo", "salomon", "reebok", "travel", "trillion", "dimitriblack",
    "generalideastandard", "hydrogen", "taylormadeapparel", "underarmour",
    "barrel", "spyder",
]

EXTRACT_JS = """() => {
    const result = {};
    const ldScript = document.querySelector('script[type="application/ld+json"]');
    if (ldScript) { try { result.ld = JSON.parse(ldScript.textContent); } catch {} }
    const metas = {};
    document.querySelectorAll('meta[property]').forEach(m => {
        const p = m.getAttribute('property');
        if (p) metas[p] = m.content;
    });
    result.meta = metas;
    const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l);
    const info = {};
    const keys = ['품번','시즌','성별','조회수','누적판매','좋아요'];
    for (let i = 0; i < lines.length; i++) {
        for (const key of keys) {
            if (lines[i] === key && i + 1 < lines.length && lines[i+1].length < 100) {
                info[key] = lines[i + 1];
            }
        }
    }
    result.info = info;
    const imgs = Array.from(document.querySelectorAll('img'))
        .map(i => i.src || '')
        .filter(s => s.includes('msscdn.net/images/') || s.includes('msscdn.net/thumbnails/'));
    const hiRes = imgs.map(u => u.replace('/thumbnails/', '/').replace(/_\\d+\\./, '_500.'));
    result.detailImages = [...new Set(hiRes)].slice(0, 8);
    const title = document.title || '';
    const colorMatch = title.match(/\\[([^\\]]+)\\]/);
    result.color = colorMatch ? colorMatch[1] : '';
    return result;
}"""


def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    # Ensure columns exist (safe for existing table)
    for col in ["style_name TEXT", "colors TEXT"]:
        try:
            conn.execute(f"ALTER TABLE musinsa_products ADD COLUMN {col}")
        except:
            pass
    conn.execute("CREATE INDEX IF NOT EXISTS idx_musinsa_brand ON musinsa_products(brand_slug)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_musinsa_style ON musinsa_products(style_name)")
    conn.commit()
    conn.close()


def extract_style_name(product_name: str) -> tuple[str, str]:
    """상품명에서 [컬러] 분리 → (스타일명, 컬러)."""
    # Pattern: "상품명 [컬러]" or "상품명_컬러"
    m = re.match(r"^(.+?)\s*\[([^\]]+)\]\s*$", product_name)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return product_name.strip(), ""


async def crawl_brand(page, brand_slug: str, max_scroll: int = 25) -> list[dict]:
    url = f"https://www.musinsa.com/brand/{brand_slug}/products"
    print(f"  [{brand_slug}] Loading: {url}")

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print(f"  [{brand_slug}] Page load failed: {str(e)[:50]}")
        return []

    await asyncio.sleep(3)

    # Scroll to load all products
    for i in range(max_scroll):
        prev = await page.evaluate("document.body.scrollHeight")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.2)
        curr = await page.evaluate("document.body.scrollHeight")
        if curr == prev:
            break

    product_urls = await page.evaluate("""() => {
        const links = Array.from(document.querySelectorAll('a[href*="/products/"]'));
        return [...new Set(links.map(a => a.href).filter(h => /\\/products\\/\\d+/.test(h)))];
    }""")

    print(f"  [{brand_slug}] Found {len(product_urls)} products")
    products = []

    for i, purl in enumerate(product_urls):
        try:
            await page.goto(purl, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(1.8)

            data = await page.evaluate(EXTRACT_JS)

            ld = data.get("ld", {})
            meta = data.get("meta", {})
            info = data.get("info", {})
            name = ld.get("name", "")
            if not name:
                continue

            style_name, color_from_name = extract_style_name(name)
            color = data.get("color", "") or color_from_name

            agg = ld.get("aggregateRating", {})
            offers = ld.get("offers", {})
            brand_name = ld.get("brand", {}).get("name", "") or brand_slug

            pid = hashlib.md5(f"musinsa:{brand_slug}:{purl}".encode()).hexdigest()[:16]

            products.append({
                "id": pid,
                "brand_slug": brand_slug,
                "brand_name": brand_name,
                "product_code": info.get("품번", ""),
                "product_name": name,
                "style_name": style_name,
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
                "color": color,
                "description": meta.get("og:description", "")[:300],
                "view_count": info.get("조회수", ""),
                "sell_count": info.get("누적판매", ""),
                "like_count": info.get("좋아요", ""),
            })

            if (i + 1) % 20 == 0:
                print(f"  [{brand_slug}] {i+1}/{len(product_urls)}...")

        except Exception as e:
            continue

    print(f"  [{brand_slug}] Collected: {len(products)}")
    return products


def save_products(products: list[dict]):
    if not products:
        return
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    for p in products:
        c.execute("""
            INSERT OR REPLACE INTO musinsa_products
            (id, brand_slug, brand_name, product_code, product_name, style_name,
             price, original_price, sale_rate, image_url, detail_images, product_url,
             rating, review_count, season, gender, color, description,
             view_count, sell_count, like_count)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            p["id"], p["brand_slug"], p["brand_name"], p["product_code"],
            p["product_name"], p["style_name"], p["price"], p["original_price"],
            p["sale_rate"], p["image_url"], p["detail_images"], p["product_url"],
            p["rating"], p["review_count"], p["season"], p["gender"],
            p["color"], p["description"], p["view_count"], p["sell_count"],
            p["like_count"],
        ))
    conn.commit()

    # Color grouping: update 'colors' field for same style_name
    brand = products[0]["brand_slug"]
    c.execute("""
        UPDATE musinsa_products SET colors = (
            SELECT GROUP_CONCAT(color, ', ')
            FROM (
                SELECT DISTINCT color
                FROM musinsa_products AS mp2
                WHERE mp2.brand_slug = musinsa_products.brand_slug
                  AND mp2.style_name = musinsa_products.style_name
                  AND mp2.color != ''
            )
        )
        WHERE brand_slug = ?
    """, (brand,))
    conn.commit()
    conn.close()


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
        for i, slug in enumerate(TOP50_BRANDS):
            print(f"\n{'='*50}")
            print(f"[{i+1}/50] {slug}")
            products = await crawl_brand(page, slug)
            save_products(products)
            total += len(products)
            await asyncio.sleep(2)

        await browser.close()

    # Summary
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        SELECT brand_name, COUNT(*) as total,
               COUNT(DISTINCT style_name) as styles,
               COUNT(NULLIF(season,'')) as with_season
        FROM musinsa_products GROUP BY brand_name ORDER BY total DESC
    """)
    print(f"\n{'='*60}")
    print(f"DONE: {total} products crawled")
    print(f"\n{'Brand':<30} {'Total':>6} {'Styles':>7} {'Season':>7}")
    print("-" * 55)
    grand_total = 0
    grand_styles = 0
    for r in c.fetchall():
        print(f"{r[0]:<30} {r[1]:>6} {r[2]:>7} {r[3]:>7}")
        grand_total += r[1]
        grand_styles += r[2]
    print("-" * 55)
    print(f"{'TOTAL':<30} {grand_total:>6} {grand_styles:>7}")
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
