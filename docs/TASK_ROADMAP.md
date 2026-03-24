# FTIB 태스크 로드맵

> 작성일: 2026-03-24
> 목표: 데이터 수집 → 키워드 매칭 → 전문가 리포트 연동 → 예측 검증

---

## 현재 완료 상태

| 영역 | 완료 항목 | 수치 |
|------|----------|------|
| 마켓 크롤링 | 28개 브랜드 수집 완료 | 7,542 상품 |
| 런웨이 수집 | 38 디자이너 × 6 시즌 | 10,930 룩 |
| VLM 라벨링 | 전체 완료 (97.3%) | 10,631 라벨 |
| 대시보드 UI | 7개 페이지 | Production 배포 |
| 크롤러 인프라 | Cafe24/Shopify/Custom/Stealth | 20+ 크롤러 |

---

## Phase 2: 키워드 매칭 + 데이터 보강 (3/24 ~ 4/4)

### Task 2-1: 런웨이↔마켓 동의어 매핑 사전 구축
> VLM 영문 키워드와 마켓 한글 메타데이터 간의 어휘 갭 해소

- **작업**: VLM 키워드 Top 100 추출 → 마켓 메타데이터 매칭 규칙 정의
- **예시**: navy↔네이비/DEEP NAVY, leather↔가죽/레더/PU, oversized↔오버핏/루즈핏
- **산출물**: `backend/utils/synonym_map.py` 확장, 매칭률 Before/After 측정
- **난이도**: 중
- **예상 소요**: 3~4시간
- **Due**: 3/26 (수)

### Task 2-2: Trend Flow check 실데이터 고도화
> 현재 expert/celeb/search 시그널이 mock → 최소 1개 실데이터 연결

- **작업**: VLM 키워드 전 시즌 확장 (현재 26SS/26FW만) + 시즌별 트렌드 변화 추적
- **산출물**: `/api/trendflow-check/keywords` 응답에 전 시즌 VLM 데이터 반영
- **난이도**: 낮
- **예상 소요**: 2시간
- **Due**: 3/27 (목)

### Task 2-3: Brand Board 트렌드 칩 매칭률 개선
> 동의어 매핑 적용 후 Brand Board Runway Trend Keywords 칩의 market_count 정확도 향상

- **작업**: Task 2-1 결과를 `trendflow_check.py`의 `_match_keyword_in_product`에 적용
- **산출물**: 칩별 매칭 상품 수 증가 검증
- **의존**: Task 2-1 완료 후
- **난이도**: 낮
- **예상 소요**: 1시간
- **Due**: 3/27 (목)

### Task 2-4: 미수집 브랜드 추가 (🟡 탐색 필요 8개)
> Carhartt WIP, Black Yak, Goldwin, COMOLI, AURALEE, New Era, Snow Peak, Palace

- **작업**: 각 사이트별 셀렉터 탐색 + 크롤러 구현
- **예상 수집**: ~200~400 상품 추가
- **난이도**: 중 (사이트별 30분~1시간)
- **예상 소요**: 6~8시간
- **Due**: 3/31 (월)

---

## Phase 3: 전문가 리포트 파이프라인 (4/1 ~ 4/11)

### Task 3-1: WGSN 리포트 파싱 파이프라인
> PDF → Claude API → 구조화된 JSON (키워드, 신뢰도, 카테고리)

- **작업**: `scripts/expert_report_pipeline.py` 구현
- **프롬프트 설계**: Catwalk Analytics / Big Ideas·STEPIC / Core Item Update 3종
- **파일럿**: 업로드된 WGSN 4개 리포트
- **산출물**: `expert_reports` + `expert_keywords` 테이블에 데이터 적재
- **난이도**: 높
- **예상 소요**: 8~12시간
- **Due**: 4/4 (금)

### Task 3-2: Trend Flow Stage 2 연동
> 파싱된 전문가 키워드를 Trend Flow check UI에 연결

- **작업**: `expert_keywords` → Trend Flow check의 expert 시그널에 실데이터 반영
- **의존**: Task 3-1 완료 후
- **난이도**: 중
- **예상 소요**: 3~4시간
- **Due**: 4/7 (월)

### Task 3-3: DB 스키마 확장
> `designer_season_insights`, `cross_pattern_log` 테이블

- **작업**: DDL 추가 + API 엔드포인트 구현
- **의존**: Task 3-1 병행 가능
- **난이도**: 중
- **예상 소요**: 2~3시간
- **Due**: 4/4 (금)

### Task 3-4: NotebookLM 교차 분석
> 리포트 간 교차 패턴 발견 (디자이너 프로파일)

- **작업**: 파싱 결과를 NotebookLM에 업로드 → 교차 인사이트 추출
- **산출물**: `designer_profiles` 작성, 주요 발견사항 문서화
- **의존**: Task 3-1 완료 후
- **난이도**: 중
- **예상 소요**: 4~6시간
- **Due**: 4/11 (금)

---

## Phase 4: 예측 엔진 + 검증 (4/14 ~ 4/25)

### Task 4-1: Trend Flow Stage 5 — 규칙 기반 예측
> 런웨이×마켓 2×2 매트릭스 기반 키워드 분류

- **작업**: Expanding / Emerging / Peak / Shrinking 자동 분류 로직
- **로직**: runway_strength × market_strength 기반
- **산출물**: `forecast-mock` → 실데이터 예측 API
- **난이도**: 중
- **예상 소요**: 4~6시간
- **Due**: 4/18 (금)

### Task 4-2: 키워드 사후 검증 (Retrospective)
> Pool A/B 키워드의 실제 마켓 반영 여부 검증

- **작업**: SS26 키워드 → FW26 마켓 데이터 교차 검증
- **산출물**: `keyword_retrospectives` 테이블에 정확도 기록
- **난이도**: 중
- **예상 소요**: 3~4시간
- **Due**: 4/25 (금)

### Task 4-3: 검색량 데이터 연동 (Stage 3 대안)
> Google Trends / Naver DataLab API 연결

- **작업**: 키워드별 검색 볼륨 추이 수집 + search 시그널 실데이터화
- **난이도**: 중~높 (API 제한 대응)
- **예상 소요**: 6~8시간
- **Due**: 4/25 (금)

---

## Phase 5: 인프라 + 확장 (4/28~)

### Task 5-1: Hyperbrowser 도입
> WAF 차단 브랜드 5개 (COS, Salomon, ASICS, K2, KAPITAL) + lazy-load 3개 (Ami, MK, ADER)

- **작업**: Hyperbrowser API 키 확보 + 크롤러 연동
- **비용**: ~$30~50/월
- **Due**: 5/2 (금)

### Task 5-2: Snowflake 마이그레이션
> SQLite → Snowflake (팀 공유, 동시 접근, 대용량 대응)

- **Due**: 5/9 (금) — 별도 계획 필요

### Task 5-3: 프론트엔드 코드 스플리팅
> 번들 ~920KB → 코드 스플리팅으로 초기 로딩 개선

- **Due**: 5/9 (금)

---

## 타임라인 요약

```
3월 4주 (3/24~28)
├── Task 2-1: 동의어 매핑 사전 구축 ────────── Due 3/26
├── Task 2-2: Trend Flow 전 시즌 VLM 확장 ──── Due 3/27
└── Task 2-3: Brand Board 매칭률 개선 ────────── Due 3/27

3월 5주 ~ 4월 1주 (3/31~4/4)
├── Task 2-4: 미수집 브랜드 추가 (🟡 8개) ──── Due 3/31
├── Task 3-1: WGSN 리포트 파이프라인 ─────────── Due 4/4
└── Task 3-3: DB 스키마 확장 ────────────────── Due 4/4

4월 2주 (4/7~11)
├── Task 3-2: Trend Flow Stage 2 연동 ────────── Due 4/7
└── Task 3-4: NotebookLM 교차 분석 ──────────── Due 4/11

4월 3~4주 (4/14~25)
├── Task 4-1: 예측 엔진 (Stage 5) ──────────── Due 4/18
├── Task 4-2: 키워드 사후 검증 ───────────────── Due 4/25
└── Task 4-3: 검색량 데이터 연동 ──────────────── Due 4/25

5월 (4/28~)
├── Task 5-1: Hyperbrowser 도입 ──────────────── Due 5/2
├── Task 5-2: Snowflake 마이그레이션 ─────────── Due 5/9
└── Task 5-3: 프론트엔드 최적화 ──────────────── Due 5/9
```

---

## 의존성 다이어그램

```
Task 2-1 (동의어) ─→ Task 2-3 (매칭률) ─→ Task 4-2 (사후검증)
                                            ↑
Task 3-1 (리포트) ─→ Task 3-2 (Stage 2) ───┘
                  ─→ Task 3-4 (NotebookLM)

Task 2-2 (VLM확장) ─→ Task 4-1 (예측엔진)
Task 2-4 (브랜드추가) — 독립 (병행 가능)
Task 4-3 (검색량) — 독립 (병행 가능)
```

---

## 리스크

| 리스크 | 영향 | 대응 |
|--------|------|------|
| WGSN 리포트 파싱 정확도 낮음 | Stage 2 데이터 품질 | 프롬프트 반복 튜닝, 수동 검증 병행 |
| 동의어 매핑 커버리지 부족 | 매칭률 미개선 | 상위 50 키워드 우선 + 점진 확장 |
| 검색량 API rate limit | Stage 3 데이터 수집 지연 | 배치 처리 + 캐싱 |
| Hyperbrowser 비용 | 월 $30~50 지속 비용 | 필요 브랜드만 선별 사용 |
