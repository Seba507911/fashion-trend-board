# 마켓 브랜드 확장 계획

> 작성일: 2026-03-26 (업데이트: 2026-03-26)
> 현재: 35개 브랜드, 11,368 상품 (+Ami Paris 644, +COVERNAT 188)

---

## Part 1: 미수집 브랜드 보완 방안 (34개)

### 🟡 Shopify JSON API 시도 가능 (6개)

Shopify 기반이면 `/products.json` API가 있을 가능성 높음.
Totême/The Row/Nanushka 패턴으로 즉시 시도 가능.

| 브랜드 | 이전 차단 사유 | 보완 방법 | 비고 |
|--------|-------------|----------|------|
| **Ami Paris** | headless lazy-load | `/products.json` API 직접 시도 | Shopify 확인됨 |
| **Maison Kitsuné** | headless 미로드 | Magento API 또는 sitemap.xml 파싱 | Magento 기반 |
| **Alanui** | 미시도 | `/products.json` 시도 | 사이트 접근 OK |
| **Low Classic** | 사이트 응답 0B | 대안 도메인 탐색 + `/products.json` | Cafe24 추정 |
| **Palace** | /shop 404 | `/products.json` 시도 (드롭 방식이라 재고 적을 수 있음) | Shopify 추정 |
| **RRL** | RL 하위 404 | RL `/products.json`에서 RRL 태그 필터 | RL Shopify 확인 |

### 🔴 Hyperbrowser 필요 (5개)

playwright-stealth로도 뚫리지 않는 강력한 WAF. **Hyperbrowser ($30~50/월)** 도입 시 해결 가능.

| 브랜드 | WAF 타입 | Hyperbrowser 가능성 | 비고 |
|--------|---------|-------------------|------|
| **COS** | Akamai | ✅ 높음 (Akamai 우회 사례 많음) | H&M 그룹, SPA 핵심 |
| **Salomon** | PerimeterX | ✅ 높음 | 러닝코어/고프코어 핵심 |
| **ASICS** | Akamai | ✅ 높음 | 이전부터 차단 |
| **K2** | 자체 SSL+접근제한 | ◐ 중간 (SSL 문제가 핵심) | 국내 아웃도어 |
| **KAPITAL** | CloudFront | ✅ 높음 | 일본 워크웨어 |

### 🟠 DemandWare/자체 플랫폼 — 커스텀 대응 필요 (8개)

API 없이 사이트 구조를 직접 파악해야 함. 사이트별 30분~1시간 탐색 필요.

| 브랜드 | 플랫폼 | 커스텀 방법 | 난이도 | 비고 |
|--------|--------|-----------|--------|------|
| **Human Made** | DemandWare | 사이트맵 파싱 또는 검색 API | 중 | 일본 스트리트 핵심 |
| **UNIQLO** | 자체 | 내부 API 탐색 (JSON 응답 확인) | 높 | SPA, URL 패턴 변경 |
| **Carhartt WIP** | 자체 (대용량 SPA) | Shadow DOM 또는 API 인터셉트 | 높 | 워크웨어 대표 |
| **Black Yak** | 고방몰 | JS 렌더링 대기 + 셀렉터 탐색 | 중 | 국내 아웃도어 |
| **New Era** | 자체 | 상품 목록 셀렉터 탐색 | 중 | 캡/헤드웨어 |
| **Snow Peak** | 자체 | 카테고리 URL + 셀렉터 탐색 | 중 | 아웃도어/라이프스타일 |
| **Columbia** | 자체 | 사이트 차단 여부 재확인 | 중 | 매스 아웃도어 |
| **Goldwin** | 자체 SPA | 카테고리 네비 구조 탐색 | 높 | 일본 테크웨어 |

### ⚫ 접근 불가 — 사이트 자체 문제 (9개)

| 브랜드 | 문제 | 가능 대안 | 비고 |
|--------|------|----------|------|
| **Jacquemus** | 사이트 점검/리뉴얼 중 | 시간 두고 재시도 | Capital-driven 대표 |
| **WOOYOUNGMI** | Cafe24 404 | 도메인/URL 재확인 | 한국 디자이너 |
| **ADER Error** | 리다이렉트 루프 | Hyperbrowser 시도 | 한국 하이프 |
| **RECTO** | DNS 실패 | 정확한 도메인 탐색 | 한국 컨템 |
| **Kangol** | 타임아웃 | 사이트 다운 가능성, 재시도 | 캡 브랜드 |
| **COMOLI** | 404 | 사이트 구조 변경, 일본 현지 도메인 확인 | 일본 미니멀 |
| **AURALEE** | 404 | 컬렉션 URL 패턴 재탐색 | 일본 컨템 |
| **visvim** | 사이트 리뉴얼 | 시간 두고 재시도 | 일본 레전드 |
| **Needles** | 접근 안 됨 | 일본 현지 프록시 필요할 수 있음 | 일본 스트리트 |

### 📌 상품 수 부족 — 보강 필요 (7개)

| 브랜드 | 현재 | 예상 전체 | 보강 방법 |
|--------|------|----------|----------|
| **H&M** | 7 | ~500+ | stealth 카테고리 URL 재탐색, Hyperbrowser |
| **Ralph Lauren** | 9 | ~300+ | stealth 스크롤 개선 또는 Shopify JSON API |
| **Patagonia** | 4 | ~200+ | 카테고리 URL 확장 + 스크롤 |
| **DEPOUND** | 134 | ~200+ | 카테고리 추가 (현재 bag/acc만) |
| **Lululemon** | 40 | ~300+ | 카테고리 URL 패턴 수정 |
| **Acne Studios** | 46 | ~200+ | headless 대기 시간 증가 |
| **Dunst** | 65 | ~150+ | 이미지 수정 필요 (0개) |

---

## Part 2: 신규 브랜드 추천 (조닝별 보강)

### 🔴 SPA/매스 — 현재 2개만 (Zara 2,768 + H&M 7)

데이터 신뢰도 확보를 위해 최소 4~5개 SPA 필요.

| 브랜드 | 플랫폼 | 예상 상품 | 수집 난이도 | 추천 이유 |
|--------|--------|----------|-----------|----------|
| **& Other Stories** | H&M 그룹 자체 | ~300 | 중 | 컨템 SPA, H&M 그룹 비교 |
| **ARKET** | H&M 그룹 자체 | ~200 | 중 | 미니멀 SPA |
| **MANGO** | mango.com | ~500 | 중 | 유러피안 SPA 대표 |
| **COS** | Akamai WAF | ~400 | 높 (Hyperbrowser) | 미니멀 SPA 핵심 |
| **UNIQLO** | 자체 | ~1,000+ | 높 | 기능성/기본템 대표 |

### 🟡 캐주얼/스트리트 — 현재 12개 (1,957 상품)

국내 무신사 인기 브랜드 보강 필요.

| 브랜드 | 플랫폼 | 예상 상품 | 수집 난이도 | 추천 이유 |
|--------|--------|----------|-----------|----------|
| **COVERNAT** | Cafe24 (covernat.net) | ~200 | 낮 (config만) | 무신사 #1 스트리트 |
| **Yale** | Cafe24 (wordsstore.co.kr) | ~150 | 낮 | 아이비리그 캐주얼 |
| **LMC** | Cafe24 | ~150 | 낮 | Lost Management Cities |
| **IAB Studio** | 자체 | ~100 | 중 | 하이프 스트리트 |
| **CPGN Studio** | Cafe24 | ~100 | 낮 | 캐주얼 |
| **Carhartt WIP** | 자체 SPA | ~300 | 높 | 워크웨어 대표 |

### 🟡 럭셔리/컨템포러리 — 현재 7개 (3,098 상품)

좋은 커버리지. 추가 시 영향력 있는 브랜드 위주.

| 브랜드 | 플랫폼 | 예상 상품 | 수집 난이도 | 추천 이유 |
|--------|--------|----------|-----------|----------|
| **Ami Paris** | Shopify | ~300 | 낮 (JSON API) | 프렌치 컨템 핵심 |
| **Jacquemus** | DemandWare | ~200 | 높 (점검중) | Capital-driven 대표 |
| **Alanui** | 자체 | ~100 | 중 | 니트웨어 전문 |
| **JW Anderson** | Shopify? | ~200 | 중 | 실험적 디자인 |

### 🟡 스포츠/아웃도어 — 현재 10개 (2,437 상품)

러닝코어/고프코어 트렌드 브랜드 보강.

| 브랜드 | 플랫폼 | 예상 상품 | 수집 난이도 | 추천 이유 |
|--------|--------|----------|-----------|----------|
| **Salomon** | WAF (PerimeterX) | ~300 | 높 (Hyperbrowser) | 고프코어→러닝 핵심 |
| **HOKA** | DemandWare? | ~200 | 높 | 러닝코어 핵심 |
| **Arc'teryx** | WAF | ~300 | 높 | 고프코어 #1 |
| **Columbia** | 자체 | ~200 | 중 | 매스 아웃도어 |
| **K2** | SSL 문제 | ~200 | 중 | 국내 아웃도어 |
| **Black Yak** | 고방몰 | ~200 | 중 | 국내 아웃도어 |
| **Discovery** | F&F 자사 | ~300 | 중 | F&F 브랜드, 필수 |

### 🟡 일본 — 현재 1개 (nanamica 170)

가장 부족한 조닝. 트렌드 참조 가치 높음.

| 브랜드 | 플랫폼 | 예상 상품 | 수집 난이도 | 추천 이유 |
|--------|--------|----------|-----------|----------|
| **Needles** | 자체 | ~200 | 중~높 | 버터플라이 트랙팬츠, 일본 스트리트 |
| **BEAMS** | 자체 | ~500 | 중 | 일본 셀렉트샵, 트렌드 인디케이터 |
| **UNITED ARROWS** | 자체 | ~400 | 중 | 일본 셀렉트샵 |
| **Kenzo** | 자체 | ~300 | 중 | LVMH, 일본 오리진 |
| **Goldwin** | 자체 SPA | ~200 | 높 | 테크웨어/nanamica 모회사 |

---

## 우선순위 제안

### 즉시 (이번 주)
1. ~~**Ami Paris** — Shopify JSON API `/products.json` 시도~~ ✅ **완료 (644 상품, EUR 가격 포함)**
2. ~~**COVERNAT** — Cafe24 config 추가~~ ✅ **완료 (188 상품, KRW 가격+이미지)**
3. **Yale** — wordsstore.co.kr 도메인 접근 불가, 대안 도메인 탐색 필요
4. **RRL** — ralphlauren.com `/products.json` 307 리다이렉트, 비 Shopify 확인
5. **H&M** — shop-by-product URL도 stealth로 0개 추출, **Hyperbrowser 필요**
6. **Lululemon** — 카테고리 URL 추가했으나 +11개만 추가 (51), **Hyperbrowser 필요**

### 다음 주 (Hyperbrowser 도입 후)
7. **COS, Salomon** — Hyperbrowser로 WAF 우회
8. **H&M, Lululemon** — Hyperbrowser 전환 (stealth로는 한계)
9. **ADER Error** — Hyperbrowser 재시도
10. **HOKA, Arc'teryx** — Hyperbrowser

### 4월 1~2주 (커스텀 크롤러)
11. **Human Made, Carhartt WIP, UNIQLO** — 사이트별 API/구조 탐색
12. **BEAMS, UNITED ARROWS** — 일본 셀렉트샵
13. **Discovery, Black Yak, K2** — 국내 아웃도어
