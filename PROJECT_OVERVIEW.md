# FTIB — Fashion Trend Intelligence Board

> 패션 트렌드 전파를 데이터 기반으로 추적하는 대시보드
> 최종 업데이트: 2026-03-26

---

## 1. 프로젝트 비전

트렌드가 **어디에서 시작(Origin)**되어 **어떤 경로로 전파**되는지를 정량적으로 추적.

```
런웨이 시그널 → 전문가 검증 → 셀럽 채택 → 마켓 확산 → 다음 시즌 예측
```

4가지 Origin 타입별 전파 패턴을 정의하고, 각 경로의 시그널을 데이터로 검증.

| Origin 타입 | 전파 경로 | 지배 조닝 |
|------------|----------|----------|
| **Runway-led** | 런웨이 → 전문가 → 셀럽 → 검색 → 마켓 (6~12M) | 럭셔리 |
| **Capital-driven** | 브랜드투자 → 캠페인 → 검색폭발 → 마켓 | 스포츠, 캐주얼 |
| **Viral/Meme** | 소셜밈 → 틱톡 → 검색급등 → 마켓 소진 | 캐주얼/스트리트 |
| **Market-organic** | 소비자수요 → 마켓 점진확대 → 검색 완만상승 | 스포츠/아웃도어 |

Market-organic은 3가지 서브타입으로 세분화:
- **Lifestyle-shift**: 라이프스타일 변화 (캠핑→고프코어, 러닝→러닝코어)
- **Necessity-driven**: 외부 환경 강제 (한파→롱패딩, 폭염→냉감소재)
- **Event-triggered**: 예측 불가 충격 (코로나→스웨트셋업/라운지웨어)

---

## 2. 기술 스택

| 레이어 | 기술 |
|--------|------|
| **Frontend** | React 18 + Vite + Tailwind CSS v4 + react-router-dom v7 |
| **Backend** | FastAPI (Python 3.9) + SQLite (aiosqlite) |
| **Charts** | Recharts, react-force-graph-2d |
| **크롤링** | Playwright + playwright-stealth (WAF 우회), requests+BS4 |
| **VLM** | Claude Vision Sonnet (`claude-sonnet-4-20250514`) |
| **배포** | GitHub + Vercel (static + serverless) |
| **환경변수** | `.env` (ANTHROPIC_API_KEY), python-dotenv |

---

## 3. 데이터 현황

### 3-1. 마켓 상품 — 11,368 스타일, 35 브랜드

| 조닝 | 브랜드 | 상품 수 | 크롤러 타입 |
|------|--------|---------|-----------|
| **SPA / 매스** | | | |
| | ZARA | 2,768 | stealth + API intercept |
| | H&M | 7 | stealth (Hyperbrowser 필요) |
| **럭셔리 / 컨템포러리** | | | |
| | Totême | 984 | Shopify JSON API |
| | The Row | 944 | Shopify JSON API |
| | Ami Paris | 644 | Shopify JSON API |
| | Nanushka | 488 | Shopify JSON API |
| | BODE | 317 | Shopify JSON API (enriched) |
| | Lemaire | 269 | Shopify |
| | Acne Studios | 46 | Custom Playwright |
| **스포츠 / 아웃도어** | | | |
| | Descente Korea | 815 | Playwright + detail |
| | Nike | 645 | Playwright + scroll |
| | Kolon Sport | 286 | requests + Apollo GraphQL |
| | nanamica | 170 | Custom Playwright |
| | New Balance | 168 | Playwright |
| | On Running | 135 | stealth + Nuxt |
| | NorthFace Korea | 122 | Playwright + detail |
| | ALO Yoga | 86 | Shopify |
| | FILA Korea | 84 | Shopify |
| | Lululemon | 51 | Playwright (Hyperbrowser 필요) |
| | SKIMS | 26 | Custom Playwright |
| **캐주얼 / 스트리트** | | | |
| | Youth | 540 | Cafe24 |
| | COVERNAT | 188 | Cafe24 |
| | Mardi Mercredi | 188 | Cafe24 |
| | Marithe | 182 | Cafe24 |
| | Blankroom | 176 | Cafe24 |
| | AMOMENTO | 175 | Cafe24 |
| | Coor | 155 | Cafe24 |
| | Stüssy | 151 | Shopify |
| | Supreme | 148 | Custom Playwright |
| | DEPOUND | 134 | Custom Playwright |
| | EMIS | 130 | Cafe24 |
| | thisisneverthat | 68 | Playwright SPA |
| | Dunst | 65 | Cafe24 |
| | Ralph Lauren | 9 | stealth |
| **일본 컨템포러리** | | | |
| | nanamica | 170 | Custom Playwright |

### 3-2. 런웨이 데이터 — 11,905 룩

- **소스**: TagWalk (requests + BeautifulSoup)
- **디자이너**: 54명 5티어 (Prada, Chanel, Dior, Balenciaga, Gucci, Coperni, Wales Bonner, Wooyoungmi 등)
- **시즌**: 24SS, 24FW, 25SS, 25FW, 26SS, 26FW

### 3-3. VLM 라벨링 — ✅ 완료 (11,455/11,905, 96.2%)

- **모델**: Claude Vision Sonnet (`claude-sonnet-4-20250514`)
- **비용**: ~$89 (입력 17.3M + 출력 2.5M tokens)
- **소요 시간**: ~4시간
- **라벨 구조**: items(아이템별 shape/size/color/texture), overall_silhouette, dominant_colors, key_materials
- **에러**: 450건 (이미지 로드 실패, 3.8%)

### 3-4. 미수집 브랜드 (27개 등록, TBA)

| 사유 | 브랜드 |
|------|--------|
| **WAF 차단** | COS, Salomon, K2, KAPITAL, ASICS |
| **사이트 점검/DNS** | Jacquemus, WOOYOUNGMI, ADER Error, RECTO |
| **Shopify 커스텀** | Maison Kitsuné |
| **SPA/JS 렌더링** | Carhartt WIP, HOKA, Black Yak, Goldwin, UNIQLO |
| **일본 (탐색 필요)** | COMOLI, AURALEE, DANTON, A.PRESSE, visvim, CAPTAIN SUNSHINE |
| **기타** | New Era, Kangol, Snow Peak, RRL, Palace |

> 관리 문서: `docs/BRAND_EXPANSION_PLAN.md`

---

## 4. 카테고리 체계

```
의류 (Wear)                    용품 (Accessory)
├── outer (아우터)              ├── headwear (모자)
├── inner (상의)                ├── bag (가방)
├── bottom (하의)               ├── shoes (신발)
└── wear_etc (기타의류)          └── acc_etc (기타용품)
```

---

## 5. 대시보드 페이지 (7개)

### 5-1. Market Brand Board (`/`)
- 25개 브랜드 상품 그리드 (카테고리별 섹션 정렬)
- **Runway Trend Keywords 칩**: VLM 런웨이 키워드 → 마켓 매칭 필터
  - 컬러(rose), 소재(emerald), 실루엣(violet) 색상 코딩
  - 클릭 시 `?keyword=` 파라미터로 상품 필터링
- 사이드바: 조닝별 브랜드 하이어라키 (수집 완료만 표시 + TBA 접이식)

### 5-2. Trend Flow (`/flow`) — Origin Framework
- **Origin별 시그널 플로우**: 2행 배치 SVG 순서도 (draw.io 스타일 베지어 화살표)
- **조닝별 Origin 분포**: 2×2 그리드 카드 (럭셔리/스포츠/캐주얼/SPA)
- **통합 타임라인 비교**: 4 Origin 수평 바 차트 (구분선 + 컬러 라벨)
- **Market-organic 서브타입**: Lifestyle-shift / Necessity-driven / Event-triggered 카드

### 5-3. Trend Flow check(Test) (`/flow-check`) — 4단계 drill-down
- Level 1: 시즌 pill + 조닝 pill 필터
- Level 2: 카테고리 탭 + 뷰 전환 (카드 / 매트릭스 / 타임라인)
- Level 3: 키워드 카드 그리드 (Confidence 순, 5 시그널 도트)
- Level 4: 상세 패널 (시그널 바, 시즌 타임라인, 마켓 브랜드 분포)
- **데이터 소스**: VLM 라벨 (runway, 실데이터) + 마켓 텍스트 매칭 (실데이터) + expert/celeb/search (mock)

### 5-4. Runway (`/runway`)
- 디자이너별 룩 그리드, 시즌/태그 필터
- `?tag=&season=` 파라미터로 Trend Flow에서 연결
- VLM 뷰어 (`/vlm`): 라벨링된 룩의 items, silhouette, colors, materials 시각화

### 5-5. Trend Analysis (`/trend`)
- 마켓 데이터 기반 KPI (탑 컬러, 소재, 핏)
- 컬러 버블 차트, 브랜드×소재 히트맵
- VLM 모드: 런웨이 데이터 기반 분석 (디자이너별 컬러/실루엣/텍스처)

### 5-6. Graph View (`/graph`)
- force-directed graph (브랜드-소재-컬러-카테고리 관계)
- Runway(VLM) / Market Brand 모드 전환
- 노드 클릭 → 연결 상세 패널

---

## 6. 크롤러 아키텍처

| 타입 | 설명 | 브랜드 |
|------|------|--------|
| **Cafe24** | config dict만 추가 | Marithe, Coor, Youth, Blankroom, Mardi, Emis, Dunst, AMOMENTO, COVERNAT |
| **Shopify** | config dict만 추가 | ALO, Lemaire, Stüssy, FILA |
| **Shopify JSON API** | `/products.json` API | Nanushka, Totême, The Row, Ami Paris, Bode |
| **Custom (Playwright)** | 브랜드별 크롤러 파일 | Nike, NorthFace, Descente, NB, Lululemon, Acne, On Running, TNT, Supreme, SKIMS, DEPOUND, nanamica |
| **Stealth (WAF 우회)** | playwright-stealth 적용 | Zara (API 인터셉트), H&M, On Running, Ralph Lauren |
| **Apollo GraphQL** | requests + __NEXT_DATA__ | Kolon Sport |

### 크롤러 데이터 품질 관리
- Coor: 결제/배송 안내 description 필터링
- Youth: 품절 오버레이/위시버튼 이미지 제거
- NorthFace/Descente: fold 버튼 클릭 후 소재/설명 파싱
- Nike: 소재 탭 클릭 + 텍스트 패턴 추출
- 전체: protocol-relative URL (`//`) → `https://` 정규화, placeholder 이미지 정리

---

## 7. 크로스 페이지 연결

```
Trend Flow check → Brand Board:  /?keyword=burgundy
Trend Flow check → Runway:       /runway?tag=burgundy&season=26SS
Brand Board → Trend Flow:        Trend Keywords 칩 → 키워드 필터
Brand Board → Runway:            (향후) 상품 카드에서 런웨이 룩 연결
```

---

## 8. 진행 상황

### ✅ 완료

**인프라**
- [x] FastAPI + React + Vite + Tailwind v4 프로젝트 구조
- [x] SQLite DB 스키마 + 카테고리 체계 (8 중분류)
- [x] Vercel 배포 파이프라인 (프로젝트 루트 배포)
- [x] 환경변수 관리 (.env + python-dotenv)

**데이터 수집**
- [x] Cafe24/Shopify/Custom 크롤러 프레임워크 (35개 브랜드, 11,368 상품)
- [x] Shopify JSON API 패턴 도입 (Nanushka/Totême/TheRow/Ami/Bode — Playwright 불필요)
- [x] playwright-stealth WAF 우회 (Zara API 인터셉트 등)
- [x] 런웨이 크롤러 (TagWalk, 11,905 룩, 54 디자이너 5티어, 6 시즌)
- [x] VLM 전체 라벨링 완료 (11,455/11,905, 96.2%)
- [x] 크롤러 데이터 품질 수정 (6개 브랜드 description/image/material)
- [x] 이미지 URL 정규화 (protocol-relative, placeholder 정리)

**대시보드 UI**
- [x] 7개 페이지 UI 구현
- [x] Trend Flow: Origin별 순서도 (2행 배치, 베지어 화살표) + Market-organic 서브타입
- [x] Trend Flow: 조닝별 Origin 분포 (2×2 그리드) + 타임라인 비교 (구분선)
- [x] Trend Flow check: 4단계 drill-down (VLM + 마켓 실데이터)
- [x] Brand Board: Runway Trend Keywords 칩 필터
- [x] 사이드바: 조닝별 하이어라키 (수집 완료 브랜드 + TBA 접이식)
- [x] 크로스 페이지 네비게이션 (?keyword=, ?tag=&season=)
- [x] 카테고리 탭 정렬 (outer→inner→bottom→wear_etc→headwear→bag→shoes→acc_etc)
- [x] 가격 포맷 (KRW, USD, EUR, JPY)

### 🔶 진행 중 (W1: 3/24~28)

- [ ] **NotebookLM 전문가 리포트 분석** — WGSN 4개 리포트 시즌 예측 + 디자이너 의도 해석
- [x] **마켓 크롤링 확장** — 35개 브랜드, 11,368 상품 (Ami Paris +644, COVERNAT +188 신규)
- [x] **브랜드 확장 계획** — 미수집 34개 보완 분석 + 조닝별 신규 추천 (`docs/BRAND_EXPANSION_PLAN.md`)
- [x] **Cafe24 크롤러 개선** — ec-data-src 지연로딩, 가격 text fallback, base64 placeholder 필터

### 🔜 다음 단계 (상세: `docs/TASK_ROADMAP.md`)

**W2 (3/31~4/4): 전문가 분석 심화 + 크롤링 고도화**
- [ ] NotebookLM 교차 분석 + 인사이트 정리 (디자이너 간 수렴/발산)
- [ ] expert_report_pipeline.py 구축 (PDF→Claude API→JSON)
- [ ] Hyperbrowser 도입 + WAF 차단 브랜드 재시도

**W3 (4/7~4/11): 전문가 리포트 보강**
- [ ] Tagwalk 프리미엄 리포트 추가 (WGSN 부족 시 교차 검증)
- [ ] 크롤링 고도화 완료 (모든 수집 가능 브랜드)

**W4~5 (4/14~4/25): 종합 분석 (1차 마일스톤)**
- [ ] 종합 상관관계 분석: 전문가 예측 × 런웨이 VLM × 마켓 데이터
- [ ] Trend Flow 실데이터 통합 (expert/runway/market 3개 시그널)

**5월: 마켓드리븐 정량화**
- [ ] Market-organic 자생 트렌드 정량 지표 설계
- [ ] 예측 검증 프레임워크 (Pool A/B 사후 검증)
- [ ] 검색량 데이터 연동 (optional)

**후순위 (Backlog)**
- 동의어 매핑 사전 → 본사 라벨링 기준 팀 협의 후 진행 (협의 미시작, 진행 예정)
- Snowflake 마이그레이션 / 프론트엔드 최적화 / 실시간 알림
- [ ] 실시간 알림 (특정 키워드 마켓 등장 시)

---

## 9. 배포 정보

- **Production**: https://fashion-trend-board.vercel.app
- **GitHub**: https://github.com/Seba507911/fashion-trend-board
- **로컬 개발**: Backend :8000 / Frontend :5173, Vite proxy `/api` → localhost:8000
- **배포 명령**: `npx vercel --prod --yes` (프로젝트 루트에서 실행)
