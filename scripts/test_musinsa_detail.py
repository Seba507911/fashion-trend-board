"""무신사 상품 상세 정보 수집 가능 범위 테스트."""
from __future__ import annotations

import asyncio
import json


async def main():
    from playwright.async_api import async_playwright
    from playwright_stealth import Stealth

    stealth = Stealth()
    async with async_playwright() as pw:
        stealth.hook_playwright_context(pw)
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900}, locale="ko-KR"
        )
        page = await ctx.new_page()

        # Test multiple product types
        test_products = [
            "https://www.musinsa.com/products/5884072",  # 무신사스탠다드 폴로셔츠
            "https://www.musinsa.com/products/5860715",  # 무신사스탠다드 데님셔츠
        ]

        for url in test_products:
            print(f"\n{'='*70}")
            print(f"URL: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)

            # Scroll down to load detail section
            for _ in range(5):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)

            detail = await page.evaluate("""() => {
                const result = {};

                // 1. JSON-LD
                const ldScript = document.querySelector('script[type="application/ld+json"]');
                if (ldScript) {
                    try { result.jsonLd = JSON.parse(ldScript.textContent); } catch {}
                }

                // 2. All meta tags (product related)
                const metas = Array.from(document.querySelectorAll('meta[property]'));
                result.metaTags = {};
                metas.forEach(m => {
                    const prop = m.getAttribute('property');
                    if (prop && (prop.includes('product') || prop.includes('og:'))) {
                        result.metaTags[prop] = m.content;
                    }
                });

                // 3. Product images (all)
                const allImgs = Array.from(document.querySelectorAll('img'))
                    .map(i => ({src: i.src || '', alt: i.alt || '', width: i.naturalWidth}))
                    .filter(i => i.src.includes('msscdn.net') || i.src.includes('musinsa.com'));
                result.images = allImgs.slice(0, 10);

                // 4. Full page text analysis - find structured info
                const body = document.body.innerText;
                const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);

                // Product info pairs (key: value patterns)
                const infoKeys = ['품번', '시즌', '성별', '조회수', '누적판매', '좋아요',
                    '색상', '사이즈', '소재', '제조국', '세탁방법', '제조사', '제조년월',
                    '혼용률', '겉감', '안감', 'A/S', '취급시'];
                const productInfo = {};
                for (let i = 0; i < lines.length; i++) {
                    for (const key of infoKeys) {
                        if (lines[i] === key && i + 1 < lines.length) {
                            productInfo[key] = lines[i + 1].substring(0, 100);
                        }
                        // Also check "key value" on same line
                        if (lines[i].startsWith(key + ' ') || lines[i].startsWith(key + '\\t')) {
                            productInfo[key] = lines[i].substring(key.length).trim().substring(0, 100);
                        }
                    }
                }
                result.productInfo = productInfo;

                // 5. Product detail/description section
                // Look for expandable detail area
                const detailSections = Array.from(document.querySelectorAll('[class*="detail"], [class*="description"], [class*="info"]'));
                result.detailSections = detailSections.slice(0, 5).map(el => ({
                    className: el.className.substring(0, 60),
                    text: el.innerText.substring(0, 200),
                }));

                // 6. Tags / keywords
                const tags = Array.from(document.querySelectorAll('[class*="tag"], [class*="chip"], [class*="badge"], [class*="keyword"]'));
                result.tags = tags.slice(0, 10).map(t => t.innerText.trim()).filter(t => t.length > 0 && t.length < 30);

                // 7. Color options
                const colorOptions = Array.from(document.querySelectorAll('[class*="color"], [class*="option"]'))
                    .map(el => el.innerText.trim())
                    .filter(t => t.length > 0 && t.length < 50);
                result.colorOptions = [...new Set(colorOptions)].slice(0, 10);

                // 8. Category breadcrumb
                const breadcrumb = Array.from(document.querySelectorAll('[class*="breadcrumb"] a, nav a'))
                    .map(a => a.innerText.trim())
                    .filter(t => t.length > 0 && t.length < 30);
                result.breadcrumb = breadcrumb.slice(0, 5);

                return result;
            }""")

            # Print results
            if detail.get("jsonLd"):
                ld = detail["jsonLd"]
                print(f"\n[JSON-LD]")
                print(f"  name: {ld.get('name', '')[:60]}")
                print(f"  brand: {ld.get('brand', {}).get('name', '')}")
                print(f"  price: {ld.get('offers', {}).get('price', '')}")
                print(f"  rating: {ld.get('aggregateRating', {}).get('ratingValue', '')}")
                print(f"  reviews: {ld.get('aggregateRating', {}).get('reviewCount', '')}")
                print(f"  image: {ld.get('image', '')[:80]}")

            if detail.get("metaTags"):
                print(f"\n[Meta Tags]")
                for k, v in detail["metaTags"].items():
                    print(f"  {k}: {v[:80]}")

            if detail.get("productInfo"):
                print(f"\n[Product Info] ({len(detail['productInfo'])} fields)")
                for k, v in detail["productInfo"].items():
                    print(f"  {k}: {v}")

            if detail.get("images"):
                print(f"\n[Images] ({len(detail['images'])} found)")
                for img in detail["images"][:5]:
                    print(f"  {img['src'][:80]}... alt={img['alt'][:30]}")

            if detail.get("tags"):
                print(f"\n[Tags] {detail['tags']}")

            if detail.get("colorOptions"):
                print(f"\n[Colors] {detail['colorOptions']}")

            if detail.get("breadcrumb"):
                print(f"\n[Breadcrumb] {detail['breadcrumb']}")

            if detail.get("detailSections"):
                print(f"\n[Detail Sections] ({len(detail['detailSections'])})")
                for ds in detail["detailSections"][:3]:
                    print(f"  class: {ds['className'][:50]}")
                    print(f"  text: {ds['text'][:100]}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
