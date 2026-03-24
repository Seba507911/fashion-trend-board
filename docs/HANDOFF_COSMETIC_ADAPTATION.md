# FTIB → 코스메틱 적용 가이드

> 패션 트렌드 인텔리전스 보드(FTIB) 프로젝트를 코스메틱 도메인에 적용하기 위한 핸드오프 문서
> 작성일: 2026-03-24

---

## 1. FTIB가 뭘 하는 프로젝트인가

**한 줄 요약**: 패션 트렌드가 런웨이에서 마켓까지 전파되는 과정을 데이터로 추적하는 대시보드.

### 핵심 가설
```
시그널 발생 → 전문가 검증 → 인플루언서 채택 → 검색량 상승 → 마켓 확산
```

이 5단계 파이프라인이 **정량적으로 추적 가능**하다는 것을 검증 중.

### 트렌드 Origin 4타입
트렌드가 어디서 시작되느냐에 따라 전파 패턴이 다름:

| Origin | 패션 예시 | 코스메틱 대응 가능성 |
|--------|----------|-------------------|
| **Runway-led** | 런웨이→전문가→셀럽→마켓 (6~12M) | 뷰티 컬렉션→전문가 리뷰→셀럽 메이크업→제품 출시? |
| **Capital-driven** | 브랜드 앰배서더 캠페인→검색 폭발 | 화장품 앰배서더/광고→검색→구매 (거의 동일 패턴) |
| **Viral/Meme** | 틱톡 밈→검색 급등→마켓 빠른 소진 | 틱톡 뷰티 트렌드 (glass skin, latte makeup 등) |
| **Market-organic** | 소비자 수요→마켓 점진 성장 | 기능성 수요 (선크림, 시카 등) |

---

## 2. 우리가 만든 것 (기술적 산출물)

### 데이터 파이프라인
```
[크롤링] → [DB 저장] → [VLM 라벨링] → [API] → [대시보드]
```

| 구성요소 | 패션 | 코스메틱 적용 시 |
|---------|------|----------------|
| **마켓 크롤링** | 28개 브랜드 공식몰 (7,542 상품) | 올리브영, 시코르, 세포라, 브랜드 공식몰 |
| **런웨이 데이터** | TagWalk 38 디자이너 10,930 룩 | 뷰티 컬렉션? 아니면 다른 시그널 소스 필요 |
| **VLM 라벨링** | Claude Vision으로 룩 이미지 분석 | 제품 이미지/스와치 분석? 또는 불필요할 수 있음 |
| **전문가 리포트** | WGSN 패션 리포트 | WGSN Beauty, Mintel, Euromonitor |
| **검색량** | (예정) Google Trends | Google Trends + 네이버 데이터랩 (동일) |

### 기술 스택 (그대로 재사용 가능)
- **Backend**: FastAPI + SQLite → 동일 구조로 시작 가능
- **Frontend**: React + Vite + Tailwind → 동일
- **크롤링**: Playwright + playwright-stealth → 동일 (사이트만 다름)
- **배포**: Vercel → 동일
- **AI**: Claude API (VLM, 리포트 파싱) → 동일

---

## 3. 코스메틱에서 다르게 봐야 하는 점

### 3-1. "런웨이"에 해당하는 시그널 소스가 다름

패션은 **런웨이 컬렉션**이 명확한 선행 시그널이지만, 코스메틱은:

| 패션 | 코스메틱 대안 |
|------|------------|
| 런웨이 쇼 (디자이너 컬렉션) | **신제품 론칭** (브랜드 공식 발표) |
| TagWalk 크롤링 | **올리브영 신상 입고**, 세포라 New Arrivals |
| 시즌별 쇼 일정 (SS/FW) | **시즌 론칭 캘린더** (봄 신상, 홀리데이 컬렉션) |
| 디자이너 의도 | **브랜드 컨셉/캠페인 메시지** |

→ **제안**: "런웨이" 대신 **"론칭 시그널"** 로 재정의. 브랜드 공식 신제품 발표 + 올리브영/세포라 신상 입고를 크롤링.

### 3-2. VLM 라벨링의 역할이 다름

패션은 이미지에서 컬러/소재/실루엣을 추출해야 했지만 (메타데이터 없음), 코스메틱은:
- **제품 메타데이터가 풍부**: 성분, 카테고리, 컬러코드, SPF 등이 이미 텍스트로 있음
- **VLM이 필요한 경우**: 스와치 색상 분석, 패키지 디자인 트렌드 정도
- **대신 중요한 것**: **리뷰 텍스트 분석** (NLP) — "촉촉해요", "밀림" 등 소비자 언어

→ **제안**: VLM 대신 **리뷰 감성 분석 + 성분 트렌드 분석**에 AI 활용.

### 3-3. Origin 타입의 비중이 다름

패션은 Runway-led가 럭셔리의 핵심이지만, 코스메틱은:

| Origin | 패션 비중 | 코스메틱 예상 비중 | 예시 |
|--------|---------|----------------|------|
| Runway-led (론칭-led) | 높음 (럭셔리) | 중간 | 샤넬 뷰티 신상 → 트렌드 |
| Capital-driven | 중간 | **높음** | 앰배서더 광고가 매출 직결 |
| Viral/Meme | 중간 | **매우 높음** | 틱톡 뷰티 = 코스메틱 핵심 채널 |
| Market-organic | 높음 (스포츠) | 높음 | 기능성 (선크림, 시카, 레티놀) |

→ **제안**: **Viral/Meme과 Capital-driven의 비중을 높여** 설계. 틱톡/인스타 뷰티 트렌드 모니터링이 핵심.

### 3-4. 크롤링 대상이 다름

| 패션 | 코스메틱 |
|------|---------|
| 브랜드 공식몰 (Zara, Nike 등) | **올리브영**, 시코르, 세포라, 화해 |
| 브랜드 28개 개별 크롤링 | 플랫폼 몇 개로 대부분 커버 가능 |
| 상품별 이미지가 핵심 | 상품 + **리뷰** + **랭킹**이 핵심 |
| 가격/사이즈/컬러/소재 | 가격/용량/성분/리뷰수/평점 |

→ **제안**: 브랜드별이 아닌 **플랫폼별 크롤링** (올리브영 전체, 세포라 전체). 리뷰 데이터 수집이 핵심 차별점.

---

## 4. 코스메틱 버전 시작 가이드

### Step 1: 프로젝트 세팅 (1~2일)
```bash
# 패션 프로젝트 구조를 복사하거나, 같은 스택으로 새로 시작
# FastAPI + React + Vite + Tailwind + SQLite
```

FTIB 코드를 fork해서 시작하면 인프라(배포, DB, API 구조)를 그대로 재사용 가능.

### Step 2: DB 스키마 설계 (1일)
```sql
-- 패션의 products 테이블 대응
products(
  id, brand_id, category_id,
  product_name, price, volume,   -- 용량 추가
  ingredients TEXT,               -- 성분 (JSON array)
  rating REAL,                    -- 평점
  review_count INTEGER,           -- 리뷰 수
  image_url, product_url,
  platform TEXT,                  -- 'oliveyoung', 'sephora', 'hwahae'
  crawled_at
)

-- 패션의 runway_looks 대응 → 신제품 론칭 로그
product_launches(
  id, brand_id, product_id,
  launch_date, platform,
  initial_ranking INTEGER,
  campaign_type TEXT,             -- 'ambassador', 'viral', 'organic'
)

-- 패션의 vlm_labels 대응 → 리뷰 분석
review_analysis(
  id, product_id,
  sentiment TEXT,                 -- positive/neutral/negative
  key_phrases TEXT,               -- JSON: ["촉촉", "지속력 좋음"]
  skin_type_mentions TEXT,        -- JSON: ["건성", "지성"]
  analyzed_at
)
```

### Step 3: 크롤러 구현 (1~2주)
**우선순위**:
1. **올리브영** — 국내 최대, 카테고리별 랭킹/베스트 데이터 풍부
2. **화해** — 성분 분석 + 리뷰 데이터 최강
3. **글로우픽** — 카테고리별 랭킹
4. **세포라 코리아** — 글로벌 프리미엄

Playwright + stealth 기반 크롤러 패턴은 FTIB와 동일하게 사용 가능.

### Step 4: 전문가 리포트 연동 (2~3주)
- **WGSN Beauty** — 뷰티 트렌드 예측
- **Mintel** — 시장 분석
- **Euromonitor** — 글로벌 시장 데이터
- NotebookLM + Claude API 파이프라인은 FTIB 것을 그대로 적용 가능

### Step 5: 대시보드 구축 (2~3주)
FTIB의 7개 페이지 구조를 코스메틱에 맞게 재설계:

| FTIB 페이지 | 코스메틱 대응 |
|------------|------------|
| Market Brand Board | **올리브영/세포라 상품 보드** |
| Runway | **신제품 론칭 트래커** |
| Trend Flow | **트렌드 전파 분석** (동일 프레임워크) |
| Trend Flow check | **키워드 시그널 대시보드** |
| Trend Analysis | **성분/카테고리 트렌드 분석** |
| Graph View | **브랜드-성분-카테고리 관계 그래프** |

---

## 5. 활용 도구 가이드

### Claude 앱 (claude.ai)
- **용도**: 아이디어 논의, 전략 설계, 리포트 해석
- **팁**: 프로젝트 지식에 이 문서 + 자체 PROJECT_OVERVIEW.md 추가하면 컨텍스트 유지

### Claude Code (CLI)
- **용도**: 코딩, 크롤러 구현, DB 작업, 배포
- **팁**: CLAUDE.md 파일을 프로젝트 루트에 두면 자동으로 프로젝트 컨텍스트를 읽음
- **메모리**: `.claude/projects/.../memory/` 폴더에 프로젝트 상태 자동 저장

### NotebookLM
- **용도**: 여러 전문가 리포트 간 교차 분석, 탐색적 질문
- **팁**: 시즌/카테고리별 프로젝트 분리 → 집중 분석

---

## 6. FTIB에서 배운 교훈

### 잘 된 것
- **Playwright + stealth** 조합이 대부분의 사이트 크롤링을 해결 (WAF 우회)
- **Cafe24/Shopify 플랫폼 크롤러**로 설정만 추가하면 새 브랜드 수집 가능
- **Claude Vision VLM**이 이미지 분석에 매우 효과적 (10,000+ 이미지 자동 라벨링)
- **Vercel 배포**가 간편하고 안정적 (SQLite 파일 커밋 방식)

### 주의할 점
- **WAF 차단** — Akamai, PerimeterX는 stealth로도 안 뚫림 → Hyperbrowser 필요
- **동의어 매핑** — AI 라벨링(영문)과 마켓 데이터(한글)의 어휘 갭이 매칭의 최대 병목
- **Shopify 커스텀 테마** — 같은 Shopify라도 브랜드별 셀렉터가 달라 개별 대응 필요
- **이미지 URL** — protocol-relative(`//`), placeholder(`data:image`), lazy-load 문제 주의
- **대용량 DB** — SQLite는 7,000+ 상품 정도는 문제없지만, 10만+ 넘으면 Snowflake 고려

### 코스메틱에서 특히 중요할 것
- **리뷰 데이터가 핵심** — 패션은 이미지 중심, 코스메틱은 리뷰 텍스트가 가장 중요한 시그널
- **플랫폼 랭킹** — 올리브영 베스트 랭킹 변화 = 가장 직접적인 마켓 시그널
- **성분 트렌드** — 레티놀, 시카, 나이아신아마이드 등 성분 키워드가 패션의 소재/컬러 역할
- **틱톡/유튜브 시그널** — 코스메틱 Viral이 패션보다 훨씬 빈번하고 영향력 큼

---

## 7. 참고 리소스

- **FTIB 코드**: https://github.com/Seba507911/fashion-trend-board
- **Production 대시보드**: https://fashion-trend-board.vercel.app
- **프로젝트 전체 개요**: `PROJECT_OVERVIEW.md`
- **크롤러 아키텍처**: `CLAUDE.md` (기술 스택 + 파일 구조)
- **브랜드 관리 리스트**: `BRAND_CRAWL_LIST.md`
- **전문가 분석 계획**: `docs/EXPERT_ANALYSIS_PLAN.md`
- **태스크 로드맵**: `docs/TASK_ROADMAP.md`
