"""무신사 상품 페이지 구조 분석 테스트."""
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

        test_urls = [
            "https://www.musinsa.com/products/3783092",
            "https://www.musinsa.com/products/4240660",
        ]

        for url in test_urls:
            print(f"\n{'='*60}")
            print(f"URL: {url}")
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            print(f"Status: {resp.status}")
            await asyncio.sleep(4)

            # JSON-LD extraction
            ld_data = await page.evaluate("""() => {
                const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                return Array.from(scripts).map(s => {
                    try { return JSON.parse(s.textContent); } catch { return null; }
                }).filter(Boolean);
            }""")

            print(f"\nJSON-LD: {len(ld_data)} blocks")
            for ld in ld_data:
                print(json.dumps(ld, ensure_ascii=False, indent=2)[:500])

            # Product detail extraction
            detail = await page.evaluate("""() => {
                const body = document.body.innerText;
                const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);

                // Find material/fabric related lines
                const matKeywords = ['소재', '원단', '혼용률', '겉감', '안감', 'Material',
                    '폴리에스터', '코튼', '나일론', '레이온', '스판덱스', '울', '리넨',
                    '가죽', '레더', '시어', '레이스', 'cotton', 'polyester', 'nylon'];
                const matLines = [];
                for (let i = 0; i < lines.length; i++) {
                    for (const kw of matKeywords) {
                        if (lines[i].includes(kw)) {
                            const context = lines.slice(Math.max(0, i-1), i+3).join(' | ');
                            matLines.push(context);
                            break;
                        }
                    }
                }

                // Find product info section
                const infoKeywords = ['상품정보', '제품 상세', '상세정보', '품번', '시즌'];
                const infoLines = [];
                for (let i = 0; i < lines.length; i++) {
                    for (const kw of infoKeywords) {
                        if (lines[i].includes(kw)) {
                            const context = lines.slice(i, i+8).join(' | ');
                            infoLines.push(context);
                            break;
                        }
                    }
                }

                // Images
                const imgs = Array.from(document.querySelectorAll('img'))
                    .map(i => i.src || '')
                    .filter(s => s.includes('image.musinsa.com'));

                return {
                    title: document.title,
                    matLines: matLines.slice(0, 5),
                    infoLines: infoLines.slice(0, 3),
                    imageCount: imgs.length,
                    uniqueImages: [...new Set(imgs)].slice(0, 5),
                };
            }""")

            print(f"\nTitle: {detail['title'][:80]}")
            print(f"Images: {detail['imageCount']} ({len(detail['uniqueImages'])} unique)")
            for img in detail["uniqueImages"]:
                print(f"  {img[:100]}")

            print(f"\nMaterial info ({len(detail['matLines'])} matches):")
            for m in detail["matLines"]:
                print(f"  {m[:120]}")

            print(f"\nProduct info ({len(detail['infoLines'])} matches):")
            for info in detail["infoLines"]:
                print(f"  {info[:120]}")

        # Brand list page test
        print(f"\n{'='*60}")
        print("=== Brand list page ===")
        await page.goto(
            "https://www.musinsa.com/brand/musinsastandard/products",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        await asyncio.sleep(4)

        brand_info = await page.evaluate("""() => {
            // Product cards
            const links = Array.from(document.querySelectorAll('a[href*="/products/"]'));
            const products = links.map(a => ({
                href: a.href,
                text: a.innerText.trim().substring(0, 60),
            })).filter(p => p.text.length > 3);

            // Unique product URLs
            const urls = [...new Set(links.map(a => a.href).filter(h => h.includes('/products/')))];

            return {
                productLinks: urls.length,
                samples: products.slice(0, 5),
                pageTitle: document.title,
            };
        }""")

        print(f"Title: {brand_info['pageTitle'][:60]}")
        print(f"Product links: {brand_info['productLinks']}")
        for p in brand_info["samples"]:
            print(f"  {p['href'][-20:]} | {p['text'][:50]}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
