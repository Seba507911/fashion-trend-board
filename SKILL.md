---
name: fashion-trend-board
description: FTIB 프로젝트 스킬 — 런웨이→마켓 트렌드 전파 추적 대시보드. 크롤링, 분석, 시각화 전체를 다루는 스킬.
---

# FTIB — Claude Code Skill

## 프로젝트 컨텍스트

패션 런웨이→셀럽→마켓 흐름을 추적하는 트렌드 인텔리전스 대시보드.
사용자: F&F AX팀 소속, Snowflake/Python/SQL 능숙.
전체 기획은 `PROJECT.md` 참조.

## 핵심 원칙

1. **MVP 우선**: 동작하는 것이 먼저. SQLite로 시작.
2. **데이터 정규화**: 컬러/소재/카테고리 일관된 형태로 JSON 저장.
3. **크롤러 안정성**: 에러 시 skip, 전체 중단하지 않음, 로깅 필수.
4. **crawl-delay 준수**: robots.txt의 crawl-delay 반드시 준수.
5. **UI 디자인**: Style B (Light Editorial), Lora 폰트, 미니멀.

---

## 기술 스택

### Python 백엔드
- **Python 3.9** (venv: `./venv/bin/python`)
- **FastAPI** + **aiosqlite** — `backend/api/`
- **Playwright** (async) — 공식몰 크롤링
- **requests + BeautifulSoup** — TagWalk 등 SSR 사이트
- `from __future__ import annotations` 필수 (3.9 호환)

### React 프론트엔드
- **React 18** + **Vite** + **Tailwind CSS**
- **react-router-dom v7** — SPA 라우팅
- **TanStack Query** — API 상태 관리
- **Recharts** — 차트, **react-force-graph-2d** — 그래프

### 서버 실행
```bash
./venv/bin/python -m uvicorn backend.api.main:app --reload --port 8000
cd frontend && npm run dev  # :5173 또는 :5174
```

### 배포
```bash
git add ... && git commit && git push origin main
npx vercel --prod --yes
```
- Vercel: `@vercel/static-build` (frontend) + `@vercel/python` (FastAPI serverless)
- SQLite는 read-only (로컬에서 크롤링 후 DB 파일 포함 배포)

---

## 크롤러 아키텍처 (플랫폼 기반)

### 구조
```
backend/crawlers/
├── base_crawler.py              # BaseCrawler ABC
├── brand_configs.py             # 브랜드 레지스트리 (핵심 파일)
├── platform_crawlers/
│   ├── cafe24.py                # Cafe24 공통 크롤러
│   └── shopify.py               # Shopify 공통 크롤러
└── brand_crawlers/
    ├── newbalance.py            # 커스텀 크롤러
    ├── northface.py             # 커스텀 (무한스크롤)
    └── descente.py              # 커스텀 (AJAX 페이지네이션)
```

### 새 브랜드 추가 방법

**Cafe24 브랜드** — config만 추가:
```python
# brand_configs.py → CAFE24_BRANDS
"brand_id": {
    "brand_id": "xxx",
    "base_url": "https://xxx.com",
    "card_selector": "ul.prdList > li.xans-record-",  # 또는 "ul.thumbnail > li"
    "categories": {"outer": ["카테고리번호"], "top": ["번호"]},
    "style_tags": ["minimal"],
    "season_id": "2026SS",
    "currency": "KRW",
}
```

**Shopify 브랜드** — config만 추가:
```python
# brand_configs.py → SHOPIFY_BRANDS
"brand_id": {
    "brand_id": "xxx",
    "base_url": "https://xxx.com",
    "card_selector": "#product-grid > li",  # Dawn 테마
    "selectors": {"name": ".card__heading a", "price": ".price-item--regular", ...},
    "collections": {"slug": "category_id"},
    "currency": "EUR",
}
```

**커스텀 브랜드** — 크롤러 클래스 작성:
```python
# brand_crawlers/xxx.py → XxxCrawler(BaseCrawler)
# brand_configs.py → CUSTOM_BRANDS에 추가 + get_crawler()에 분기 추가
```

**DB 등록 필수:**
```sql
INSERT OR IGNORE INTO brands (id, name, name_kr, brand_type, website_url) VALUES (...)
```

### 크롤링 실행
```bash
python scripts/run_crawl.py --list                      # 등록 브랜드 목록
python scripts/run_crawl.py --brand xxx --dry-run        # 테스트
python scripts/run_crawl.py --brand xxx --details        # 실제 크롤링
python scripts/run_crawl.py --brand all --max-pages 10   # 전체 브랜드
```

### 등록된 브랜드 (10개)
| 브랜드 | 플랫폼 | 상품 수 | 특이사항 |
|--------|--------|---------|----------|
| marithe | Cafe24 | ~298 | 표준 Cafe24 구조 |
| coor | Cafe24 | ~201 | 표준 Cafe24 구조 |
| blankroom | Cafe24 | ~259 | `ul.thumbnail > li` 변형 셀렉터 |
| youth | Cafe24 | ~844 | 표준 Cafe24 구조 |
| alo | Shopify | ~183 | `.PlpTile` 카드 셀렉터 |
| lemaire | Shopify | ~308 | Dawn 테마, EUR 가격 (`2.900€`) |
| newbalance | Custom | ~163 | `data-*` 속성 기반 |
| northface | Custom | ~299 | 무한스크롤, Playwright 필수 |
| descente | Custom | ~988 | AJAX 페이지네이션, `.grid-item.thumb-prod` |
| asics | Custom | 0 | Akamai WAF 차단 — 보류 |

### TagWalk 런웨이 크롤러
```bash
python scripts/crawl_tagwalk.py --designers prada gucci lemaire --seasons fall-winter-2026
```
- 13 디자이너: Prada, Gucci, Lemaire, Dior, Saint Laurent, Balenciaga, Loewe, Celine, Miu Miu, Bottega Veneta, Valentino, Chanel, Hermes
- crawl-delay 2.5초, `cdn.tag-walk.com` 이미지

---

## API 엔드포인트

```
GET /api/brands                          # 브랜드 목록
GET /api/products?brand=xx&category=xx   # 상품 목록
GET /api/products/{id}                   # 상품 상세

GET /api/analysis/kpi                    # KPI (총 상품, 탑 컬러/소재/핏)
GET /api/analysis/colors                 # 컬러 분포 (전체 + 브랜드별)
GET /api/analysis/materials              # 브랜드×소재 매트릭스
GET /api/analysis/categories             # 브랜드×카테고리 분포
GET /api/analysis/graph                  # 그래프 뷰 노드/엣지

GET /api/runway?designer=xx&season=xx    # 런웨이 룩
GET /api/runway/designers                # 디자이너 목록
GET /api/runway/seasons                  # 시즌 목록

GET /api/trendflow/keywords              # 추적 키워드
GET /api/trendflow/runway-signals        # 런웨이 시그널
GET /api/trendflow/market-validation     # 마켓 검증
GET /api/trendflow/celeb-mock            # 셀럽 목업
GET /api/trendflow/expert-mock           # 전문가 리포트 목업
GET /api/trendflow/forecast-mock         # 예측 목업
```

## 프론트엔드 라우팅

| 경로 | 컴포넌트 | 설명 |
|------|----------|------|
| `/runway` | `Runway.jsx` | 런웨이 룩 갤러리 |
| `/flow` | `TrendFlow.jsx` | 트렌드 전파 파이프라인 (5단계) |
| `/` | `ProductBoard.jsx` | Market Brand Board |
| `/trend` | `TrendAnalysis.jsx` | 크로스 브랜드 트렌드 분석 |
| `/graph` | `GraphView.jsx` | Zettelkasten 그래프 뷰 |

### 새 페이지 추가 패턴
1. `frontend/src/pages/XxxPage.jsx` 생성
2. `App.jsx`에 `<Route path="/xxx" element={<XxxPage />} />` 추가
3. `Sidebar.jsx`의 `navItems`에 항목 추가
4. API 필요 시 `backend/api/routes/xxx.py` 생성 → `main.py`에 라우터 등록

---

## DB 스키마

| 테이블 | 역할 |
|--------|------|
| `brands` | 브랜드 마스터 (brand_type: own/competitor/reference) |
| `products` | 마켓 상품 3,209개 (9개 브랜드) |
| `runway_looks` | 런웨이 룩 1,345개 (13 디자이너) |
| `signals` | 시그널 시계열 |
| `scores` | 종합 스코어 |
| `predictions` | 예측 로그 |

### JSON 컬럼 처리
```python
# 저장
colors = json.dumps(["Black", "Navy"], ensure_ascii=False)
# 읽기 (None 체크 필수)
colors_list = json.loads(row["colors"]) if row["colors"] else []
```

---

## UI 디자인 규칙 (Style B — Light Editorial)

- 폰트: `Lora` (헤딩), 시스템 산세리프 (본문)
- 카드: `aspect-[2/3]` 세로형, `object-top` 크롭
- 색상: CSS 변수 (`--color-primary`, `--color-border`, etc.)
- 레이블: `text-[10px] font-semibold tracking-[1.5px] uppercase`
- 사이드바: 220px 고정
- 브랜드 색상: alo=#4ECDC4, newbalance=#E74C3C, marithe=#3498DB, coor=#5B7553, blankroom=#2C2C2C, youth=#E67E22, lemaire=#8D6E63, northface=#D32F2F, descente=#1565C0

---

## 자주 발생하는 이슈

| 이슈 | 해결 |
|------|------|
| `str \| None` 문법 에러 | `from __future__ import annotations` 추가 |
| uvicorn import 에러 | `./venv/bin/python -m uvicorn` 사용 |
| NB 컬러 `(19)BLACK` | `_clean_color()` 정규식으로 정제 |
| Cafe24 동적 로딩 | `domcontentloaded` + `sleep(5)` + 스크롤 |
| Shopify EUR 가격 `2.900€` | `.`이 천단위 구분자 → 정규식 분기 |
| Cafe24 셀렉터 변형 | `brand_configs`에 `card_selector` 지정 |
| ASICS Akamai 차단 | 해결 불가, 보류 |
| Vercel 빈 화면 | `/assets/*` 라우트를 SPA fallback 위에 배치 |
| CORS 에러 | `main.py`에서 `allow_origins=["*"]` |
