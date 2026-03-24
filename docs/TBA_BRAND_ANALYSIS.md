# TBA 브랜드 접근성 분석 리포트

> 분석일: 2026-03-24
> 도구: playwright-stealth (headless Chromium)
> 대상: 미수집 브랜드 27개

---

## 요약

| 분류 | 브랜드 수 | 설명 |
|------|----------|------|
| 🟢 **즉시 수집 가능** | 6 | 상품 카드 감지됨, 크롤러 구현만 하면 됨 |
| 🟡 **추가 탐색 필요** | 8 | 접근은 되지만 상품 카드 셀렉터를 못 찾음 |
| 🔴 **WAF 차단** | 5 | Akamai/PerimeterX/CloudFront WAF → Hyperbrowser 필요 |
| ⚫ **접근 불가** | 8 | DNS 실패, SSL 오류, 타임아웃, 404 |

---

## 🟢 즉시 수집 가능 (6개)

크롤러를 구현하면 바로 수집할 수 있는 브랜드.

| 브랜드 | URL | 카드 셀렉터 | 수량 | 비고 |
|--------|-----|-----------|------|------|
| **AMOMENTO** | amomento.kr | `a[href*=product]:140` | 140 | 도메인이 amomento.kr로 변경됨 (amfrfr.com 아님) |
| **Ami Paris** | amiparis.com/ko-kr/shopping/man | `.product-item:42` | 42 | Shopify 커스텀, 이전에 셀렉터 문제로 실패 → 재시도 가능 |
| **Maison Kitsuné** | maisonkitsune.com/kr/man/categories.html | `.product-item:40` | 40 | 메인 카테고리 페이지에서만 작동 |
| **Supreme** | supremenewyork.com/shop | `a[href*=product]:66` | 66 | /shop 전체 페이지에서 수집 가능 |
| **Dunst** | dunst.kr | `article:12` | 12 | 도메인이 dunst.kr (dunst.co.kr 아님), SSL ignore 필요 |
| **ADER Error** | adererror.com | `article:14` | 14 | 메인 페이지에서 카드 감지, 카테고리 URL 탐색 필요 |

**예상 수집량**: ~314개 상품
**작업 난이도**: 낮~중 (커스텀 Playwright 크롤러)

---

## 🟡 추가 탐색 필요 (8개)

사이트 접근은 성공하지만, 기본 셀렉터로 상품 카드를 찾지 못한 브랜드.
JS 렌더링 대기 시간 증가, 스크롤, 또는 다른 셀렉터/API 탐색 필요.

| 브랜드 | 상태 | Body 크기 | 분석 |
|--------|------|----------|------|
| **Carhartt WIP** | 200 OK | 1.4MB | 대용량 SPA, 상품이 lazy-load 또는 Shadow DOM. 더 긴 대기+스크롤 필요 |
| **Black Yak** | 200 OK | 301KB | 고방몰 플랫폼, JS 렌더링 후 상품 로드. 셀렉터 심층 탐색 필요 |
| **Goldwin** | 200 OK | 532KB | 일본 자체 플랫폼 SPA, 카테고리 네비게이션 구조 탐색 필요 |
| **COMOLI** | 200 OK | 31KB | 일본 미니멀 사이트, 상품이 다른 URL 패턴일 수 있음 |
| **AURALEE** | 200 OK | 56KB | 일본, 컬렉션/쇼핑 별도 URL 구조 탐색 필요 |
| **New Era** | 200 OK | 157KB | 국내 자체 플랫폼, 상품 목록 셀렉터 탐색 필요 |
| **Snow Peak** | 200 OK | 21KB | 국내 자체 플랫폼, 카테고리 URL 재확인 필요 |
| **Palace** | 200 OK | 31KB | /shop 페이지에서 상품 미노출, 시즌 드롭 방식이라 상시 재고가 적을 수 있음 |

**예상 조치**: 각 사이트별 15~30분 추가 탐색 → 절반 정도 수집 가능 예상

---

## 🔴 WAF 차단 (5개)

Anti-bot 시스템(Akamai, PerimeterX, CloudFront)이 headless 브라우저를 차단.
playwright-stealth로도 우회 불가. **Hyperbrowser 또는 Residential Proxy 필요**.

| 브랜드 | WAF 타입 | HTTP 응답 | 비고 |
|--------|---------|----------|------|
| **COS** | Akamai | 200 (Access Denied 페이지) | H&M 그룹, 동일 WAF |
| **Salomon** | PerimeterX | 403 | 강력한 봇 차단 |
| **ASICS** | Akamai | 403 | 이전부터 차단됨 |
| **K2** | 자체 | 403 (Invalid Connection) | SSL + 접근 제한 |
| **KAPITAL** | CloudFront | 403 | AWS WAF |

**예상 조치**: Hyperbrowser API ($30~50/월) 또는 Residential Proxy 도입 후 재시도
**대안**: 무신사/29CM 등 국내 플랫폼에서 해당 브랜드 상품 간접 수집

---

## ⚫ 접근 불가 (8개)

사이트 자체에 접근할 수 없는 브랜드.

| 브랜드 | 사유 | 상세 |
|--------|------|------|
| **RECTO** | DNS 실패 | rectostudio.com 도메인 확인 필요 (rfrfrfr.com도 실패) |
| **Kangol** | 타임아웃 | kangol.kr 응답 없음, 사이트 다운 가능성 |
| **WOOYOUNGMI** | 404 | Cafe24 기반이지만 상품 페이지 404 반환 |
| **Jacquemus** | 404 | DemandWare 기반, 사이트 점검/리뉴얼 중 |
| **UNIQLO** | 404 | 카테고리 URL 패턴 변경, 재탐색 필요 |
| **RRL** | 404 | RL 하위 카테고리, URL 구조 재확인 필요 |
| **HOKA** | 410 Gone | 한국 사이트 없음, US 사이트로 리다이렉트 |
| **visvim** | 상품 3개만 | 사이트 리뉴얼 중, 상품 극소수 노출 |

**예상 조치**: 도메인/URL 재확인 후 일부 복구 가능 (UNIQLO, RRL, HOKA US)

---

## 권장 액션 플랜

### 1순위: 즉시 크롤러 구현 (🟢 6개)
- AMOMENTO, Ami Paris, Maison Kitsuné, Supreme, Dunst, ADER Error
- 예상 소요: 2~3시간
- 예상 수집: ~314개 상품

### 2순위: 추가 탐색 후 크롤러 (🟡 일부)
- Carhartt WIP, New Era, Black Yak → 국내 브랜드 우선
- Goldwin, COMOLI, AURALEE → 일본 브랜드 (nanamica와 유사 접근)
- 예상 소요: 각 30분~1시간 탐색 + 크롤러 구현

### 3순위: Hyperbrowser 도입 (🔴 5개)
- COS, Salomon이 가장 가치 높음 (SPA 벤치마크 + 러닝코어)
- Hyperbrowser API 키 확보 후 일괄 재시도
- 비용: ~$30~50/월

### 4순위: 보류/제외 (⚫ 일부)
- Kangol, WOOYOUNGMI, Jacquemus → 사이트 정상화 후 재시도
- RECTO → 정확한 도메인 확인 필요
- HOKA → US 사이트로 대체 수집 고려
