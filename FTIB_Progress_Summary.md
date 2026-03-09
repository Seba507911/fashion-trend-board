# FTIB (Fashion Trend Intelligence Board) — 진행 요약

> 최종 업데이트: 2026-03-09

---

## 프로젝트 목적

패션 **런웨이 → 상품화 → 바이럴 → 소비** 흐름을 데이터로 추적하여, 트렌드 예측과 시장 기회를 발견하는 개인 대시보드 시스템.

### 핵심 워크플로우

1. **Runway** — 주요 패션위크 런웨이 룩을 수집하여 거시적 트렌드 사전 파악
2. **Market Brand Board** — 실제 마켓에 풀린 상품 크롤링 + 판매 시그널 점수화
3. **Trend Analysis / Graph View** — 크로스 브랜드 인사이트 도출
4. **예측-검증 루프** — 런웨이 예측 vs 실제 결과 비교 → 가중치 보정 반복

---

## 완료된 작업

### 1. 인프라 구축
- [x] 프로젝트 구조 설계 (모노레포: backend + frontend)
- [x] SQLite DB 스키마 설계 및 생성 (brands, products, runway_looks, signals, scores, predictions)
- [x] FastAPI 백엔드 서버 구축 (포트 8000)
- [x] React 18 + Vite + Tailwind CSS 프론트엔드 구축
- [x] Vite proxy 설정 (/api → backend)
- [x] react-router-dom 기반 SPA 라우팅

### 2. 마켓 브랜드 크롤링
| 브랜드 | 상품 수 | 상세 데이터 | 비고 |
|--------|--------:|-------------|------|
| ALO Yoga | ~100 | 사이즈, 컬러, 소재, 핏 | 글로벌 사이트, USD 통화 |
| New Balance | ~180 | 컬러 추출됨 | 사이즈/설명 개선 필요 |
| Marithe F. Girbaud | 360 | 사이즈, 컬러, 소재, 설명, 핏 | Cafe24 플랫폼, 완전 수집 |
| ASICS | 0 | - | Akamai 봇 차단으로 보류 |
| **합계** | **~640** | | |

### 3. 런웨이 데이터 수집 (TagWalk)
| 브랜드 | 룩 수 | 시즌 |
|--------|------:|------|
| Prada | 113 | FW26, SS26 |
| Gucci | 121 | FW26, SS26 |
| Lemaire | 52 | FW26, SS26 |
| Dior | 52 | FW26, SS26 |
| Saint Laurent | 99 | FW26, SS26 |
| Balenciaga | 134 | FW26, SS26 |
| Loewe | 119 | FW26, SS26 |
| Celine | 78 | FW26, SS26 |
| Miu Miu | 91 | FW26, SS26 |
| Bottega Veneta | 157 | FW26, SS26 |
| Valentino | 106 | FW26, SS26 |
| Chanel | 103 | FW26, SS26 |
| Hermes | 120 | FW26, SS26 |
| **합계** | **1,345** | |

### 4. 대시보드 UI 구현
- [x] **Runway 페이지** — 디자이너/시즌 필터, 그리드 갤러리, 룩 상세 모달
- [x] **Market Brand Board** — 브랜드/카테고리 필터, 세로형 카드(7~8열), 상세 모달
- [x] **Trend Analysis** — KPI 카드, 컬러 버블 차트, 브랜드별 컬러 바 차트, 소재 히트맵
- [x] **Graph View** — Force-directed 그래프, 노드 타입별 필터, 클릭 상세 패널
- [x] **사이드바** — Runway > Market Brand Board > Trend Analysis > Graph View 순서

### 5. 백엔드 API
- [x] `/api/brands` — 브랜드 CRUD
- [x] `/api/products` — 상품 목록/상세 (필터링)
- [x] `/api/analysis/kpi` — 핵심 KPI
- [x] `/api/analysis/colors` — 컬러 분포
- [x] `/api/analysis/materials` — 소재 매트릭스
- [x] `/api/analysis/graph` — 그래프 노드/엣지
- [x] `/api/runway` — 런웨이 룩 목록
- [x] `/api/runway/designers` — 디자이너 목록
- [x] `/api/runway/seasons` — 시즌 목록

### 6. 디자인 목업 (Pencil)
- [x] Style B (Light Editorial) 기반 전체 디자인 시스템
- [x] Trend Analysis Dashboard 목업
- [x] Graph View (Obsidian-style) 목업

---

## 향후 작업 (TODO)

### 우선순위: 높음
| 작업 | 설명 |
|------|------|
| 런웨이 이미지 분석 | CLIP/비전 AI로 소재, 실루엣, 카테고리, 컬러 자동 추출 |
| 스코어링 엔진 구현 | 네이버 검색량 + 무신사 랭킹 + 수기 시그널 → 상품별 점수 |
| 수기 입력 UI | 판매 판단, 셀럽 착용, 트렌드 메모 등 수기 데이터 입력 폼 |
| 예측 기록 UI | 런웨이 기반 사전 예측 입력 + 시즌 후 결과 비교 뷰 |

### 우선순위: 중간
| 작업 | 설명 |
|------|------|
| NB 크롤러 개선 | 사이즈/설명/핏 데이터 보완 |
| ASICS 대안 탐색 | Akamai 우회 또는 다른 데이터 소스 |
| 런웨이 추가 시즌 | FW25, SS25 등 과거 시즌 수집 |
| 런웨이 남성복 수집 | `--types man` 으로 남성복 컬렉션 추가 |
| Graph View 강화 | 런웨이 데이터와 마켓 데이터 연결, 시즌 간 비교 |

### 우선순위: 낮음 (장기)
| 작업 | 설명 |
|------|------|
| 무신사/W컨셉 크롤링 | 시장 존재감 측정용 데이터 |
| SNS 버즈 연동 | 인스타그램/틱톡 해시태그 모니터링 |
| 셀럽 착용 자동 트래킹 | 이미지 검색 기반 |
| 자동 리포트 생성 | 주간/월간 트렌드 리포트 자동화 |
| Snowflake 이전 | 데이터 규모 확대 시 |

---

## 기술 스택

| 영역 | 사용 기술 |
|------|-----------|
| 백엔드 | FastAPI, Python 3.9, aiosqlite, SQLite |
| 프론트엔드 | React 18, Vite, Tailwind CSS, react-router-dom v7 |
| 차트 | Recharts |
| 그래프 | react-force-graph-2d |
| 크롤링 (상품) | Playwright (async) |
| 크롤링 (런웨이) | requests + BeautifulSoup4 |
| 상태관리 | TanStack Query |
| 디자인 | Pencil MCP (.pen 파일) |

---

## 서버 실행 방법

```bash
# 1. 백엔드
source venv/bin/activate
python -m uvicorn backend.api.main:app --reload --port 8000

# 2. 프론트엔드
cd frontend && npm run dev

# 3. 접속
http://localhost:5173 (또는 5174)
```

---

## 핵심 인사이트 & 메모

- **TagWalk은 하이패션 런웨이 전용** — 스포츠/스트릿웨어 브랜드(NB, ASICS, ALO 등)는 없음
- **Cafe24 플랫폼 크롤링 패턴** — `cate_no=` 파라미터, `ul.prdList > li.xans-record-` 셀렉터, `ec-data-price` 속성
- **NB 컬러 코드 형식** — `(19)BLACK` → `_clean_color()` 함수로 정제 필요
- **ASICS는 Akamai WAF로 완전 차단** — stealth 모드, UA 변경, headed 모드 모두 실패
- **런웨이 이미지 CDN 패턴** — `cdn.tag-walk.com/{resolution}/{filename}` (list/view/zoom)
