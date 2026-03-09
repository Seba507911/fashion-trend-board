# Fashion Trend Intelligence Board (FTIB)

## 프로젝트 개요

패션 브랜드의 **런웨이 → 상품화 → 바이럴 → 소비** 흐름을 데이터로 추적하고, 시그널 기반 스코어링으로 시장 기회를 발견하는 개인 대시보드 시스템.

### 핵심 워크플로우

```
1. Runway (사전 트렌드 수집)
   └─ 주요 패션위크 런웨이 룩을 수집하여 거시적 트렌드 파악
   └─ 향후: 이미지 기반 소재/실루엣/카테고리/컬러 자동 추출

2. Market Brand Board (시장 상품 크롤링)
   └─ 실제 마켓에 풀린 상품들의 세부정보(컬러, 소재, 핏, 사이즈) 수집
   └─ 수기 판매 판단, 네이버 검색량, 무신사 랭킹, SNS 바이럴, 셀럽 착용 등 점수화

3. Trend Analysis & Graph View (인사이트 도출)
   └─ 크로스 브랜드 트렌드 분석 (컬러/소재/카테고리 분포)
   └─ 제텔카스텐 스타일 그래프로 속성 간 연결 관계 탐색

4. 예측-검증 루프 (장기 디벨롭)
   └─ 런웨이 단계에서 거시적/카테고리 단위 트렌드 사전 예측
   └─ 사후 실제 점수와 비교하여 예측 정확도 리뷰
   └─ 가중치 점수를 조정하며 꾸준히 디벨롭
```

### 3대 목적
1. **아카이빙**: 런웨이 룩 + 경쟁 브랜드 주요 상품을 수집하여 디지털 보드로 관리
2. **예측-검증 루프**: 런웨이→시장 흐름의 사전 예측과 사후 결과 비교를 통해 분석 정교화
3. **인사이트 발견**: 어떤 트렌드가 왜 폭발했는지(마케팅/셀럽/바이럴 등) 그 과정을 추적

---

## 대시보드 구조

| 탭 | 설명 | 상태 |
|----|------|------|
| **Runway** | 패션위크 런웨이 룩 갤러리 (TagWalk 소스) | 구현 완료 |
| **Market Brand Board** | 마켓 브랜드 상품 보드 (크롤링 데이터) | 구현 완료 |
| **Trend Analysis** | KPI, 컬러/소재 분포, 브랜드×소재 매트릭스 | 구현 완료 |
| **Graph View** | 브랜드-소재-컬러-카테고리 관계 그래프 | 구현 완료 |

---

## 현재 데이터 현황

### Runway (TagWalk)
| 브랜드 | 시즌 | 룩 수 |
|--------|------|------:|
| Prada | FW26, SS26 | 113 |
| Gucci | FW26, SS26 | 121 |
| Lemaire | FW26, SS26 | 52 |
| Dior | FW26, SS26 | 52 |
| Saint Laurent | FW26, SS26 | 99 |
| Balenciaga | FW26, SS26 | 134 |
| Loewe | FW26, SS26 | 119 |
| Celine | FW26, SS26 | 78 |
| Miu Miu | FW26, SS26 | 91 |
| Bottega Veneta | FW26, SS26 | 157 |
| Valentino | FW26, SS26 | 106 |
| Chanel | FW26, SS26 | 103 |
| Hermes | FW26, SS26 | 120 |
| **합계** | | **1,345** |

### Market Brand Board (공식몰 크롤링)
| 브랜드 | 상품 수 | 상세정보 |
|--------|--------:|----------|
| ALO Yoga | ~100 | 사이즈, 컬러, 소재, 핏 |
| New Balance | ~180 | 컬러 (사이즈/설명 개선 필요) |
| Marithe | 360 | 사이즈, 컬러, 소재, 설명 |
| ASICS | 0 | Akamai 봇 차단으로 보류 |
| **합계** | **~640** | |

---

## 기술 스택

| 영역 | 현재 | 확장 예정 |
|------|------|-----------|
| 크롤링 | Playwright (상품) + requests/BS4 (런웨이) | Scrapy 클러스터 |
| 백엔드 | FastAPI + Python 3.9 | FastAPI + Celery |
| DB | SQLite (aiosqlite) | PostgreSQL / Snowflake |
| 프론트엔드 | React 18 + Vite + Tailwind CSS | + D3.js, Deck.gl |
| 차트 | Recharts | + D3.js |
| 그래프 | react-force-graph-2d | + 3D, 커스텀 레이아웃 |
| 라우팅 | react-router-dom v7 | |
| 상태관리 | TanStack Query | |
| AI/ML | - | CLIP (이미지 분석), LLM (트렌드 요약) |

---

## 디렉토리 구조

```
fashion-trend-board/
├── PROJECT.md                    # 프로젝트 전체 기획서
├── SKILL.md                      # Claude Code 스킬 정의
│
├── backend/
│   ├── db/
│   │   ├── database.py           # DB 스키마 + 초기화 + 커넥션
│   │   └── ftib.db               # SQLite 데이터베이스
│   │
│   ├── crawlers/
│   │   ├── base_crawler.py       # 크롤러 추상 베이스 클래스
│   │   └── brand_crawlers/       # 브랜드별 크롤러
│   │       ├── alo.py            # ALO Yoga (aloyoga.co.kr)
│   │       ├── newbalance.py     # New Balance (nbkorea.com)
│   │       ├── marithe.py        # 마리떼 (marithe-official.com, Cafe24)
│   │       └── asics.py          # ASICS (보류 — Akamai 차단)
│   │
│   └── api/
│       ├── main.py               # FastAPI 앱 + CORS + 라우터 등록
│       └── routes/
│           ├── brands.py         # /api/brands
│           ├── products.py       # /api/products
│           ├── analysis.py       # /api/analysis (트렌드 분석)
│           └── runway.py         # /api/runway (런웨이 룩)
│
├── frontend/
│   ├── vite.config.js            # Vite + proxy (/api → :8000)
│   ├── src/
│   │   ├── App.jsx               # BrowserRouter + Routes
│   │   ├── components/
│   │   │   ├── Sidebar.jsx       # 네비게이션 사이드바
│   │   │   ├── ProductBoard.jsx  # Market Brand Board
│   │   │   ├── ProductCard.jsx   # 상품 카드 (세로형)
│   │   │   └── ProductDetail.jsx # 상품 상세 모달
│   │   ├── pages/
│   │   │   ├── Runway.jsx        # 런웨이 룩 갤러리
│   │   │   ├── TrendAnalysis.jsx # 트렌드 분석 대시보드
│   │   │   └── GraphView.jsx     # 그래프 뷰 (force-directed)
│   │   ├── hooks/
│   │   │   └── useProducts.js    # TanStack Query 훅
│   │   └── utils/
│   │       └── formatPrice.js    # 가격/스코어 포맷 유틸
│   └── public/
│
└── scripts/
    ├── run_crawl.py              # 브랜드 크롤링 실행기
    ├── crawl_tagwalk.py          # TagWalk 런웨이 크롤러
    ├── check_db.py               # DB 현황 체크
    └── inspect_*.py              # 사이트 구조 조사 스크립트들
```

---

## 스코어링 모델

### 현재 (MVP) — 향후 구현 예정
```
Total Score = (Search Buzz × 0.4) + (Market Presence × 0.3) + (Manual Signal × 0.3)
```

### 시그널 소스 (수집 예정)
| 시그널 | 설명 | 상태 |
|--------|------|------|
| 네이버 검색량 | DataLab API 키워드 검색 추이 | 미구현 |
| 무신사 랭킹 | 카테고리별 랭킹 크롤링 | 미구현 |
| SNS 바이럴 | 인스타그램/틱톡 해시태그 | 미구현 |
| 셀럽 착용 | 셀럽/인플루언서 착용 기록 | 미구현 (수기) |
| 판매 판단 | 잘 팔렸다고 판단되는 상품 표시 | 미구현 (수기) |

가중치는 예측-검증 루프를 통해 지속 보정.

---

## 서버 실행

```bash
# 백엔드 (venv 활성화 후)
source venv/bin/activate
python -m uvicorn backend.api.main:app --reload --port 8000

# 프론트엔드
cd frontend && npm run dev

# 크롤링 — 마켓 브랜드
python scripts/run_crawl.py --brand marithe --details

# 크롤링 — 런웨이 (TagWalk)
python scripts/crawl_tagwalk.py --designers prada gucci lemaire

# DB 현황 확인
python scripts/check_db.py
```

---

## 향후 로드맵

| 우선순위 | 작업 | 설명 |
|----------|------|------|
| **높음** | 런웨이 이미지 분석 | CLIP/비전 AI로 소재, 실루엣, 카테고리, 컬러 자동 추출 |
| **높음** | 스코어링 구현 | 네이버 검색량 + 무신사 랭킹 + 수기 시그널 점수화 |
| **높음** | 수기 입력 UI | 판매 판단, 셀럽 착용, 메모 등 수기 데이터 입력 |
| **중간** | 예측-검증 뷰 | 런웨이 단계 예측 → 시즌 후 결과 비교 대시보드 |
| **중간** | NB 상세 크롤러 개선 | 사이즈/설명 데이터 보완 |
| **중간** | ASICS 대안 크롤링 | API 우회 또는 다른 소스 탐색 |
| **낮음** | 무신사/W컨셉 크롤링 | 시장 존재감 측정용 |
| **낮음** | SNS 버즈 연동 | 인스타/틱톡 해시태그 모니터링 |
