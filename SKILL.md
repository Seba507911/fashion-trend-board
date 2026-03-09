---
name: fashion-trend-board
description: FTIB 프로젝트 스킬 — 런웨이 트렌드 수집부터 마켓 상품 크롤링, 트렌드 분석, 그래프 뷰까지 패션 트렌드 인텔리전스 대시보드 전체를 다루는 스킬.
---

# FTIB — Claude Code Skill

## 프로젝트 컨텍스트

패션 런웨이→마켓 흐름을 추적하는 대시보드. 사용자는 F&F AX팀 소속, Snowflake/Python/SQL 능숙.
전체 기획은 `PROJECT.md` 참조.

## 핵심 원칙

1. **MVP 우선**: 동작하는 것이 먼저. SQLite로 시작.
2. **데이터 정규화**: 컬러/소재/카테고리 일관된 형태로 저장.
3. **크롤러 안정성**: 에러 시 skip (전체 중단하지 않음), 로깅 필수.
4. **crawl-delay 준수**: robots.txt의 crawl-delay 반드시 준수.
5. **UI 디자인**: Style B (Light Editorial) 기반, Lora 폰트, 미니멀.

## 기술 스택 & 컨벤션

### Python 백엔드
- **Python 3.9** (venv: `./venv/bin/python`)
- **FastAPI** + **aiosqlite** — `backend/api/`
- **Playwright** (async) — 공식몰 크롤링
- **requests + BeautifulSoup** — TagWalk 등 SSR 사이트
- `from __future__ import annotations` 사용 (3.9 호환)
- 한국어 주석 OK, 변수/함수명은 영문

### React 프론트엔드
- **React 18** + **Vite** + **Tailwind CSS**
- **react-router-dom v7** — SPA 라우팅
- **TanStack Query** — API 상태 관리
- **Recharts** — 차트
- **react-force-graph-2d** — 그래프 시각화
- 컴포넌트: PascalCase, 유틸: camelCase

### 서버 실행
```bash
# 백엔드 (프로젝트 루트에서)
./venv/bin/python -m uvicorn backend.api.main:app --reload --port 8000

# 프론트엔드
cd frontend && npm run dev  # :5173 또는 :5174

# Vite proxy: /api → http://localhost:8000
```

## DB 스키마 핵심

| 테이블 | 역할 |
|--------|------|
| `brands` | 브랜드 마스터 (brand_type: own/competitor/reference) |
| `products` | 마켓 상품 (크롤링 데이터) |
| `runway_looks` | 런웨이 룩 (TagWalk) |
| `signals` | 시그널 시계열 |
| `scores` | 종합 스코어 |
| `predictions` | 예측 로그 |

### JSON 컬럼
`colors`, `materials`, `image_urls`, `style_tags`, `sizes` — JSON 문자열 저장:
```python
import json
colors = json.dumps(["Black", "Navy"])
colors_list = json.loads(row["colors"])  # None 체크 필수
```

## 크롤러 패턴

### 마켓 브랜드 크롤러 (Playwright)
```python
# backend/crawlers/brand_crawlers/{brand}.py
class XxxCrawler(BaseCrawler):
    def __init__(self): super().__init__("brand_id")
    async def get_product_list_urls(self, season) -> list[str]: ...
    def get_card_selector(self) -> str: ...
    async def parse_product_card(self, page, element) -> dict | None: ...
    async def parse_product_detail(self, page, url) -> dict: ...
```
- 실행: `python scripts/run_crawl.py --brand xxx --details`
- 페이지 간 2-3초 딜레이, 개별 파싱 실패 시 skip

### TagWalk 런웨이 크롤러 (requests)
```bash
python scripts/crawl_tagwalk.py --designers prada gucci --seasons fall-winter-2026
```
- crawl-delay 2.5초 준수
- `cdn.tag-walk.com/view/` (상세), `/list/` (썸네일) URL 패턴
- URL 패턴: `/en/collection/{type}/{designer}/{season}`

### 브랜드별 크롤러 메모
| 브랜드 | 플랫폼 | 특이사항 |
|--------|--------|----------|
| ALO | Shopify 기반 | `/collections/{cat}` 패턴 |
| New Balance | 자체몰 | `nbkorea.com`, 카테고리 URL 파라미터 |
| Marithe | Cafe24 | `marithe-official.com`, `cate_no=` 파라미터, `ul.prdList > li.xans-record-` |
| ASICS | 자체몰 | Akamai WAF 차단 — 보류 |

## API 엔드포인트

```
GET /api/brands                     # 브랜드 목록
GET /api/products                   # 상품 목록 (필터: brand, category, season)
GET /api/products/{id}              # 상품 상세
GET /api/analysis/kpi               # KPI (총 상품, 탑 컬러/소재/핏)
GET /api/analysis/colors            # 컬러 분포 (전체 + 브랜드별)
GET /api/analysis/materials         # 브랜드×소재 매트릭스
GET /api/analysis/graph             # 그래프 뷰 노드/엣지
GET /api/runway                     # 런웨이 룩 (필터: designer, season)
GET /api/runway/designers           # 디자이너 목록
GET /api/runway/seasons             # 시즌 목록
```

## 프론트엔드 라우팅

| 경로 | 컴포넌트 | 설명 |
|------|----------|------|
| `/runway` | `Runway.jsx` | 런웨이 룩 갤러리 |
| `/` | `ProductBoard.jsx` | Market Brand Board |
| `/trend` | `TrendAnalysis.jsx` | 트렌드 분석 |
| `/graph` | `GraphView.jsx` | 그래프 뷰 |

## UI 디자인 규칙 (Style B — Light Editorial)
- 폰트: `Lora` (헤딩), 시스템 산세리프 (본문)
- 카드: `aspect-[2/3]` 세로형, `object-top` 크롭
- 색상: CSS 변수 (`--color-primary`, `--color-border`, etc.)
- 레이블: `text-[10px] font-semibold tracking-[1.5px] uppercase`
- 사이드바: 220px 고정, DASHBOARD 섹션 라벨

## 자주 발생하는 이슈

| 이슈 | 해결 |
|------|------|
| Python 3.10+ 문법 (`str \| None`) | `from __future__ import annotations` 추가 |
| uvicorn import 에러 | `./venv/bin/python -m uvicorn` 사용 (시스템 Python 아님) |
| NB 컬러 `(19)BLACK` 형식 | `_clean_color()` 함수로 정제 |
| Cafe24 동적 로딩 | `domcontentloaded` + `asyncio.sleep(5)` + 스크롤 |
| ASICS Akamai 차단 | 현재 해결 불가, 보류 |
| CORS 에러 | `main.py`에 5173, 5174 포트 모두 등록 |
