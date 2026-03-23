# FTIB — Fashion Trend Intelligence Board

> 패션 트렌드 전파를 데이터 기반으로 추적하는 대시보드
> 최종 업데이트: 2026-03-23

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

### 3-1. 마켓 상품 — 7,155 스타일, 25 브랜드

| 조닝 | 브랜드 | 상품 수 | 크롤러 타입 |
|------|--------|---------|-----------|
| **SPA / 매스** | | | |
| | ZARA | 2,768 | stealth + API intercept |
| | H&M | 7 | stealth (일부만) |
| **럭셔리 / 컨템포러리** | | | |
| | BODE | 317 | Custom Playwright |
| | Lemaire | 197 | Shopify |
| | Acne Studios | 46 | Custom Playwright |
| **스포츠 / 아웃도어** | | | |
| | Descente Korea | 815 | Playwright + detail |
| | Nike | 645 | Playwright + scroll |
| | Kolon Sport | 223 | requests + Apollo GraphQL |
| | On Running | 135 | stealth + Nuxt |
| | NorthFace Korea | 122 | Playwright + detail |
| | ALO Yoga | 86 | Shopify |
| | FILA Korea | 84 | Shopify |
| | New Balance | 80 | Playwright |
| | Lululemon | 40 | Playwright |
| | SKIMS | 26 | Custom Playwright |
| **캐주얼 / 스트리트** | | | |
| | Youth | 528 | Cafe24 |
| | Marithe | 182 | Cafe24 |
| | Coor | 155 | Cafe24 |
| | Mardi Mercredi | 141 | Cafe24 |
| | Stüssy | 133 | Shopify |
| | Blankroom | 98 | Cafe24 |
| | EMIS | 80 | Cafe24 |
| | thisisneverthat | 68 | Playwright SPA |
| | Ralph Lauren | 9 | stealth |
| **일본 컨템포러리** | | | |
| | nanamica | 170 | Custom Playwright |

### 3-2. 런웨이 데이터 — 10,930 룩

- **소스**: TagWalk (requests + BeautifulSoup)
- **디자이너**: 38명 (Prada, Chanel, Dior, Balenciaga, Gucci 등)
- **시즌**: 24SS, 24FW, 25SS, 25FW, 26SS, 26FW

### 3-3. VLM 라벨링 — ✅ 완료 (10,631/10,930, 97.3%)

- **모델**: Claude Vision Sonnet (`claude-sonnet-4-20250514`)
- **비용**: ~$89 (입력 17.3M + 출력 2.5M tokens)
- **소요 시간**: ~4시간
- **라벨 구조**: items(아이템별 shape/size/color/texture), overall_silhouette, dominant_colors, key_materials
- **에러**: 299건 (이미지 로드 실패, 2.7%)

### 3-4. 미수집 브랜드 (30개 등록, TBA)

| 사유 | 브랜드 |
|------|--------|
| **WAF 차단** | COS, Salomon, K2, KAPITAL, ASICS |
| **사이트 점검/DNS** | Jacquemus, WOOYOUNGMI, Dunst, ADER Error, AMOMENTO, RECTO, Palace |
| **Shopify 커스텀** | Ami Paris, Maison Kitsuné |
| **SPA/JS 렌더링** | Carhartt WIP, Supreme, HOKA, Black Yak, Goldwin, UNIQLO |
| **일본 (탐색 필요)** | COMOLI, AURALEE, DANTON, A.PRESSE, visvim, CAPTAIN SUNSHINE |
| **기타** | New Era, Kangol, Snow Peak, RRL |

> 관리 문서: `BRAND_CRAWL_LIST.md`

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
| **Cafe24** | config dict만 추가 | Marithe, Coor, Youth, Blankroom, Mardi, Emis, Dunst |
| **Shopify** | config dict만 추가 | ALO, Lemaire, Stüssy, FILA |
| **Custom (Playwright)** | 브랜드별 크롤러 파일 | Nike, NorthFace, Descente, Kolon Sport, NB, Lululemon, Acne, On Running, TNT, Bode, SKIMS, nanamica |
| **Stealth (WAF 우회)** | playwright-stealth 적용 | Zara (API 인터셉트), H&M, On Running, Ralph Lauren, Ami |
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
- [x] Cafe24/Shopify/Custom 크롤러 프레임워크 (25개 브랜드, 7,155 상품)
- [x] playwright-stealth WAF 우회 (Zara API 인터셉트 등)
- [x] 런웨이 크롤러 (TagWalk, 10,930 룩, 38 디자이너, 6 시즌)
- [x] VLM 전체 라벨링 완료 (10,631/10,930, 97.3%)
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

### 🔶 진행 중

- [ ] 런웨이↔마켓 키워드 매칭 강화 (VLM 영문 키워드 vs 마켓 한글 메타데이터 어휘 갭)
  - 동의어 매핑 사전 확장 필요 (navy↔네이비, leather↔가죽/레더 등)
  - VLM 라벨링 완료했으므로 매칭 테이블 구축 가능

### 🔜 다음 단계

**데이터 확장**
- [ ] Hyperbrowser로 WAF 차단 브랜드 재시도 (COS, Salomon, K2 등)
- [ ] 일본 브랜드 크롤링 확대 (COMOLI, AURALEE, visvim 등)
- [ ] 미수집 브랜드 30개 순차 대응 (BRAND_CRAWL_LIST.md 참고)
- [ ] Ralph Lauren 상품 수 개선 (현재 9개, lazy-load 대응 필요)
- [ ] H&M 카테고리 확장 (현재 7개, 일부 카테고리만 작동)

**Trend Flow 실데이터 연결**
- [ ] Stage 2 (Expert Report): PDF 업로드 → Claude API 키워드 추출, 또는 수동 입력 폼
- [ ] Stage 3 (Celebrity): Google Trends / Naver DataLab 검색량 데이터 연동
- [ ] Stage 5 (Forecast): Stage 1~4 기반 규칙 엔진
  - Expanding: 런웨이↑ + 마켓↑
  - Emerging: 런웨이↑ + 마켓↓ (아직 마켓 미반영)
  - Peak: 런웨이↓ + 마켓↑ (소진 중)
  - Shrinking: 런웨이↓ + 마켓↓

**분석 고도화**
- [ ] Market-organic 서브타입 자동 분류 (외부 데이터 연동)
  - Lifestyle-shift: 스포츠 참여율, 캠핑장 예약 추이
  - Necessity-driven: 기상 데이터, 미세먼지 지표
  - Event-triggered: 볼륨 급증 탐지 알고리즘
- [ ] 키워드별 시즌 간 트렌드 변화 추적 (SS→FW 비교)
- [ ] 가격 트렌드 분석 (시즌별 가격대 변화)

**기술 개선**
- [ ] Snowflake 연동 (SQLite → Snowflake 마이그레이션)
- [ ] 프론트엔드 코드 스플리팅 (번들 ~920KB)
- [ ] 자연어 트렌드 브리핑 자동 생성 (Claude API)
- [ ] 실시간 알림 (특정 키워드 마켓 등장 시)

---

## 9. 배포 정보

- **Production**: https://fashion-trend-board.vercel.app
- **GitHub**: https://github.com/Seba507911/fashion-trend-board
- **로컬 개발**: Backend :8000 / Frontend :5173, Vite proxy `/api` → localhost:8000
- **배포 명령**: `npx vercel --prod --yes` (프로젝트 루트에서 실행)
