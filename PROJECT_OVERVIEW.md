---
name: FTIB Project Overview
description: Full architecture, data status, feature status, and ideation for Fashion Trend Intelligence Board
type: project
---

# FTIB 프로젝트 전체 개요

## 1. 프로젝트 비전

**Fashion Trend Intelligence Board (FTIB)**는 패션 트렌드가 런웨이에서 시장까지 전파되는 과정을 데이터 기반으로 추적·분석하는 대시보드.

핵심 가설: `런웨이 시그널 → 전문가 검증 → 셀럽/인플루언서 채택 → 마켓 확산 → 다음 시즌 예측`의 5단계 파이프라인으로 트렌드 전파를 정량화.

---

## 2. 현재 아키텍처

```
┌─────────────────────────────────────────────────┐
│  Frontend (React 18 + Vite + Tailwind CSS v4)   │
│  ├── Sidebar (조닝별 브랜드 하이어라키 + TBA)      │
│  ├── Market Brand Board (/) + Trend Chips        │
│  ├── Trend Flow (/flow) — Origin Framework       │
│  ├── Trend Flow check(Test) (/flow-check)        │
│  ├── Runway (/runway) + VLM Test (/vlm)          │
│  ├── Trend Analysis (/trend)                     │
│  └── Graph View (/graph)                         │
├─────────────────────────────────────────────────┤
│  Backend (FastAPI + SQLite/aiosqlite)            │
│  ├── /api/products (keyword 필터, 카테고리 정렬)  │
│  ├── /api/runway (tag/season 필터)                │
│  ├── /api/trendflow (5-stage pipeline)            │
│  ├── /api/trendflow-check (VLM+마켓 실데이터)     │
│  │   ├── /keywords, /keyword/{kw}/detail          │
│  │   └── /trend-chips (Brand Board용)             │
│  ├── /api/analysis + /api/vlm                     │
│  └── Crawlers (23 brands, 3 platforms + custom)   │
├─────────────────────────────────────────────────┤
│  Deploy: Vercel (static + serverless)             │
│  DB: SQLite (ftib.db, committed to git)           │
│  VLM: Claude Vision Sonnet (vlm_pilot.py)         │
│  WAF: playwright-stealth (Zara, H&M, On, RL)     │
└─────────────────────────────────────────────────┘
```

---

## 3. 데이터 현황 (2026-03-19)

### 마켓 상품 데이터 (~7,100 스타일, 25 브랜드)

| 조닝 | 브랜드 | 스타일 수 | 크롤러 |
|------|--------|-----------|--------|
| SPA | Zara | 2,768 | stealth + API intercept |
| 스포츠 | Descente | 815 | Playwright + detail |
| 스포츠 | Nike | 645 | Playwright + scroll |
| 캐주얼 | Youth | 528 | Cafe24 |
| 스포츠 | Kolon Sport | 223 | requests + Apollo GraphQL |
| 럭셔리 | Lemaire | 197 | Shopify |
| 캐주얼 | Marithe | 182 | Cafe24 |
| 일본 | nanamica | 170 | Playwright |
| 캐주얼 | Coor | 155 | Cafe24 |
| 캐주얼 | Mardi Mercredi | 141 | Cafe24 |
| 스포츠 | On Running | 135 | stealth + Nuxt |
| 캐주얼 | Stussy | 133 | Shopify |
| 스포츠 | NorthFace | 122 | Playwright + detail |
| 캐주얼 | Blankroom | 98 | Cafe24 |
| 스포츠 | ALO Yoga | 86 | Shopify |
| 스포츠 | FILA | 84 | Shopify |
| 캐주얼 | Emis | 80 | Cafe24 |
| 스포츠 | New Balance | 80 | Playwright |
| 캐주얼 | thisisneverthat | 68 | Playwright SPA |
| 럭셔리 | Acne Studios | 46 | Playwright |
| 스포츠 | Lululemon | 40 | Playwright |
| 캐주얼 | Ralph Lauren | 9 | stealth (개선 필요) |
| SPA | H&M | 7 | stealth (일부만) |
| 럭셔리 | Bode | 317 | Custom Playwright |
| 스포츠 | SKIMS | 26 | Custom Playwright |

### 런웨이 데이터 (10,930 룩, 38 디자이너, 6 시즌)
- 소스: TagWalk (requests + BS4)
- 시즌: 24SS, 24FW, 25SS, 25FW, 26SS, 26FW
- VLM 라벨: ~6,150/10,930 (53%) 진행 중 (Claude Sonnet Vision, 예상 ~2시간 남음)

### TBA 브랜드 (25+ 등록됨, 미수집)
- WAF 차단: COS, Salomon, K2, KAPITAL
- 사이트 점검/DNS: Jacquemus, WOOYOUNGMI, Dunst, ADER Error, AMOMENTO, RECTO
- Hyperbrowser 필요: COS, Salomon 등
- 관리 문서: BRAND_CRAWL_LIST.md

---

## 4. 페이지별 상세

### Market Brand Board (/) — 트렌드 키워드 필터 포함
- 브랜드별 상품 그리드 (카테고리별 섹션 정렬)
- **Runway Trend Keywords 칩**: VLM 키워드 → 마켓 매칭 필터
- 카테고리 탭: outer → inner → bottom → wear_etc → headwear → bag → shoes → acc_etc
- 크로스 페이지: ?keyword= 파라미터로 Trend Flow에서 연결

### Trend Flow check(Test) (/flow-check) — 4단계 drill-down
- Level 1: 시즌 pill + 조닝 pill 필터
- Level 2: 카테고리 탭 + 뷰 전환 (카드/매트릭스/타임라인)
- Level 3: 키워드 카드 그리드 (Confidence 순, 5 시그널 도트)
- Level 4: 상세 패널 (시그널 바, 시즌 타임라인, 마켓 브랜드)
- 데이터: VLM 라벨 (runway) + 텍스트 매칭 (market) + mock (expert/celeb/search)

### Trend Flow (/flow) — Origin Framework
- Origin별 시그널 플로우 (SVG 다이어그램)
- 조닝별 Origin 분포 (4개 조닝 카드)
- 통합 타임라인 비교 (4 Origin 수평 바)

### Runway (/runway) + VLM Test (/vlm)
- 디자이너별 룩 그리드, 시즌/태그 필터
- ?tag=&season= 파라미터로 Trend Flow에서 연결
- VLM 뷰어: 라벨링된 룩의 items, silhouette, colors, materials 표시

---

## 5. 아이디어 / 다음 단계

### 런웨이↔마켓 키워드 매칭 강화 (핵심 과제)
- **문제**: VLM 키워드(영문)와 마켓 메타데이터(한글/코드)의 어휘 갭
  - navy ↔ 네이비/DEEP NAVY/(19)NVY
  - oversized ↔ 오버핏/루즈핏/릴렉스드
  - leather ↔ 가죽/레더/PU/합성가죽
- **해결**: 동의어 매핑 사전 확장 + 마켓 상품 텍스트 정규화
- **방법**: VLM 라벨링 전량 완료 후, 매칭 테이블 구축

### Trend Flow 실데이터 확보
- Stage 2 (Expert): PDF 업로드 → Claude API 키워드 추출, 또는 수동 입력 폼
- Stage 3 (Celebrity): Google Trends / Naver DataLab 검색량 대안
- Stage 5 (Forecast): Stage 1~4 기반 규칙 엔진 (Expanding/Emerging/Peak/Shrinking)

### 마켓 상품 VLM 불필요
- 마켓 상품은 이미 colors/materials/product_name 메타데이터가 있음
- 텍스트 매칭만으로 충분 (동의어 매핑 확장이 관건)
- VLM은 런웨이 룩(이미지만 존재)에만 적용

### 향후 고려
- [ ] Market-organic 서브타입 세분화 (`market_lifestyle`, `market_necessity`, `market_event`)
  - Lifestyle-shift: 라이프스타일 변화 기반 (캠핑→고프코어, 러닝→러닝화 일상화)
  - Necessity-driven: 외부 환경 강제 (한파→롱패딩, 폭염→냉감소재)
  - Event-triggered: 예측 불가 충격 (코로나→스웨트셋업), 이벤트 종료 후 일부 정착/소멸
  - 모니터링: 각각 외부 데이터(스포츠 참여율, 기상, 이벤트 감지) 연동 필요
- [ ] Snowflake 연동 (SQLite → Snowflake 마이그레이션)
- [ ] 실시간 알림 (특정 키워드 마켓 등장 시)
- [ ] 가격 트렌드 분석 (시즌별 가격대 변화)
- [ ] 자연어 트렌드 브리핑 자동 생성 (Claude API)
- [ ] 프론트엔드 코드 스플리팅 (번들 ~920KB)

---

## 6. 진행 사항 체크리스트

### ✅ 완료
- [x] FastAPI + React + Vite + Tailwind v4 프로젝트 구조
- [x] DB 스키마 + 카테고리 체계 (8 중분류: Wear 4 + Accessory 4)
- [x] Cafe24/Shopify/Custom 크롤러 프레임워크 (23 브랜드)
- [x] playwright-stealth WAF 우회 (Zara API 인터셉트, H&M, On, RL)
- [x] 런웨이 크롤러 (TagWalk, 10,930 룩)
- [x] VLM 파일럿 → 전체 라벨링 진행 중 (Claude Sonnet Vision)
- [x] 7개 페이지 UI (Brand Board, Trend Flow ×2, Runway ×2, Analysis, Graph)
- [x] Trend Flow check: 4단계 drill-down (VLM + 마켓 실데이터)
- [x] Brand Board: Runway Trend Keywords 칩 필터
- [x] 사이드바: 조닝별 하이어라키 + TBA 섹션
- [x] 크로스 페이지 네비게이션 (?keyword=, ?tag=&season=)
- [x] 크롤러 데이터 품질 수정 (6개 브랜드 description/image/material)
- [x] 이미지 URL 정규화 (protocol-relative, placeholder 정리)
- [x] Vercel 배포 파이프라인

### 🔶 진행 중
- [ ] VLM 전체 라벨링 (10,930 룩, ~$89) — 53% 완료, ~2시간 남음
- [ ] 런웨이↔마켓 키워드 매칭 강화 (동의어 매핑)

### 🔜 다음 단계
- [ ] Trend Flow Stage 2/3/5 실데이터 연결
- [ ] Hyperbrowser로 WAF 차단 브랜드 재시도
- [ ] 일본 브랜드 크롤링 확대 (COMOLI, AURALEE, visvim 등)
