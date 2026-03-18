# FTIB Project — Claude Code Skill

> 이 파일을 프로젝트 루트에 CLAUDE.md로 복사하면 Claude Code가 자동으로 읽습니다.

## 프로젝트 개요

Fashion Trend Intelligence Board — 패션 트렌드 전파를 데이터 기반으로 추적하는 대시보드.
트렌드가 어디에서 시작(Origin)되어 어떤 경로로 전파되는지를 정량적으로 추적.

## 기술 스택

- **Backend**: FastAPI (Python 3.9, `from __future__ import annotations` 필수)
- **Frontend**: React 18 + Vite + Tailwind CSS v4 + react-router-dom v7
- **Database**: SQLite (aiosqlite, Vercel 서버리스 호환)
- **Charts**: Recharts, react-force-graph-2d
- **배포**: GitHub + Vercel (`npx vercel --prod --yes` from project root, NOT frontend/)
- **크롤링**: Playwright + playwright-stealth (WAF 우회), requests+BS4 (Kolon Sport GraphQL)
- **VLM**: Claude Vision Sonnet (`claude-sonnet-4-20250514`), `scripts/vlm_pilot.py`
- **환경변수**: `.env` (ANTHROPIC_API_KEY), `python-dotenv`로 로드

## 핵심 개념

### Origin 4타입 — 각각 다른 전파 경로

```
Runway-led:     런웨이 → 전문가 → 셀럽 → 검색 → 마켓   (순차, 6~12M)
Capital-driven: 브랜드투자 → 캠페인 → 검색폭발 → 마켓   (런웨이/전문가 건너뜀)
Viral/Meme:     소셜밈 → 틱톡확산 → 검색급등 → 마켓소진  (전통채널 우회)
Market-organic: 소비자수요 → 마켓점진확대 → 검색완만상승  (선행시그널 없음)
```

### 패션 조닝 (수집 완료 브랜드)

| zoning | 브랜드 | 지배 Origin |
|--------|--------|-----------|
| 럭셔리/컨템포러리 | Lemaire(197), Acne Studios(46) | runway_led |
| 스포츠/아웃도어 (글로벌) | Nike(645), NB(80), On Running(135), Lululemon(40), ALO(86) | market_organic |
| 스포츠/아웃도어 (국내) | Descente(815), NorthFace(122), Kolon Sport(223), FILA(84) | market_organic |
| 캐주얼/스트리트 (글로벌) | Stussy(133), Ralph Lauren(9) | viral, capital_driven |
| 캐주얼/스트리트 (국내) | Youth(528), Marithe(182), Coor(155), Blankroom(98), Mardi(141), TNT(68), Emis(80) | viral, capital_driven |
| SPA/매스 | Zara(2,768), H&M(7) | 전체 팔로우 |
| 일본 컨템포러리 | nanamica(170) | runway_led |

### 키워드 풀 A/B

- **풀 A**: 런웨이 Top 30 ∩ 전문가 리포트 (합의된 시그널)
- **풀 B**: 전문가 리포트 − 런웨이 (독립 예측)

### Confidence 지표

키워드별 5개 시그널(전문가, 런웨이, 셀럽, 검색, 마켓) 종합 점수 (0~100%)

---

## Trend Flow 메인 대시보드 — UI 상세 스펙 ⭐

### 4단계 drill-down 구조

```
Level 1: 필터 바 (시즌 + 조닝)
  ↓ 범위를 좁힘
Level 2: 카테고리 탭 (전체 / 컬러 / 소재 / 실루엣 / 아이템 / 스타일)
  ↓ 관심 영역 선택
Level 3: 키워드 카드 그리드 (Confidence 순 정렬)
  ↓ 키워드 클릭
Level 4: Keyword Detail Panel (시그널 바 + 타임라인 + 마켓 + 보정)
```

### Level 1: 필터 바

```jsx
// 시즌 선택 (pill 토글, 단일 선택)
seasons = ['24SS', '24FW', '25SS', '25FW', '26SS', '26FW']

// 조닝 필터 (pill 토글, 단일 선택)
zonings = ['전체', '럭셔리', '스포츠/아웃도어', '캐주얼/스트리트', 'SPA/매스']
```

### Level 2: 카테고리 탭

```jsx
// 탭 (카테고리별 필터)
categories = ['전체', '컬러', '소재', '실루엣', '아이템', '스타일']

// 뷰 전환 토글 (같은 데이터, 다른 시각화)
views = ['카드 뷰', '매트릭스 뷰', '타임라인 뷰']
// 카드 뷰: 기본 — Confidence 순 그리드
// 매트릭스 뷰: 런웨이 강도 × 마켓 매칭률 2×2 매트릭스
// 타임라인 뷰: 시즌별 전파 비교 타임라인
```

### Level 3: 키워드 카드

각 카드에 표시할 정보:

```jsx
<KeywordCard>
  <Top>
    <KeywordName>burgundy</KeywordName>
    <ConfidenceBadge value={85} />  // 초록(70+), 노랑(40-69), 회색(0-39)
  </Top>
  
  <SignalDots>
    // 5개 시그널의 강도를 도트로 표시
    // on(파란) = 강한 시그널, weak(회색) = 약한 시그널, off(빈) = 없음
    <Dot label="전문가" status="on|weak|off" />
    <Dot label="런웨이" status="on|weak|off" />
    <Dot label="셀럽"   status="on|weak|off" />
    <Dot label="검색"   status="on|weak|off" />
    <Dot label="마켓"   status="on|weak|off" />
  </SignalDots>
  
  <Tags>
    <CategoryTag>color | material | silhouette | item | style</CategoryTag>
    <OriginTag>Runway-led | Capital | Viral | Organic | —</OriginTag>
    <PoolTag>풀 A | 풀 B</PoolTag>
  </Tags>
</KeywordCard>
```

그리드 레이아웃: `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`
정렬: Confidence 내림차순 (기본)

### Level 4: Keyword Detail Panel

키워드 카드 클릭 시 그리드 아래에 패널이 열림:

```jsx
<KeywordDetailPanel keyword="burgundy">
  <Header>
    <Title>burgundy</Title>
    <Subtitle>color · Runway-led · 풀 A · Confidence 85%</Subtitle>
    <CloseButton />
  </Header>
  
  <Section title="시그널 강도">
    // 5개 시그널 바 (수평 바 차트)
    <SignalBar label="전문가" value={0.8} detail="WGSN + Pantone" />
    <SignalBar label="런웨이" value={0.9} detail="12 디자이너" />
    <SignalBar label="셀럽"   value={0.45} detail="스파이크 2건" />
    <SignalBar label="검색"   value={0.65} detail="+45% vs 전기" />
    <SignalBar label="마켓"   value={0.55} detail="47개 상품" />
  </Section>
  
  <Section title="시즌별 전파 타임라인">
    // 수평 바 차트, 시즌별 시그널 누적
    <TimelineBar season="24FW" width={20} label="런웨이 5" />
    <TimelineBar season="25SS" width={40} label="런웨이 8 · WGSN" />
    <TimelineBar season="25FW" width={70} label="+셀럽 · 마켓 23개" />
    <TimelineBar season="26SS" width={90} label="마켓 47개 · 검색 +45%" />
  </Section>
  
  <Section title="마켓 브랜드 분포">
    // 클릭 시 Brand Board로 이동 (?keyword=burgundy&brand=nike)
    <BrandPill brand="Nike" count={12} />
    <BrandPill brand="Descente" count={8} />
    <BrandPill brand="Youth" count={7} />
    ...
  </Section>
  
  <Actions>
    <Button onClick={navigateToRunway}>런웨이 룩 보기</Button>
    <Button onClick={navigateToBrandBoard}>마켓 상품 보기</Button>
    <Button onClick={evaluate('agree')}>동의</Button>
    <Button onClick={evaluate('disagree')}>비동의</Button>
    <Button onClick={openComment}>코멘트</Button>
  </Actions>
</KeywordDetailPanel>
```

### 페이지 간 연결

```
Trend Flow → Brand Board: /market?keyword=burgundy
Trend Flow → Runway: /runway?tag=burgundy&season=26SS
Brand Board → Trend Flow: 상품 카드에 "Trend Flow에서 보기" 링크
```

### 매트릭스 뷰 (뷰 전환 시)

```
         런웨이 강         런웨이 약
마켓 강  [확산 중]          [마켓 자생]
         burgundy(85%)     gorpcore(55%)
         tailoring(78%)    
         
마켓 약  [잠재 시그널]      [미확인]
         sheer(62%)        cobalt blue(28%)
         ballet flats(51%)
```

각 셀에 해당 키워드 카드가 배치됨. 카드 클릭 → Detail Panel 열림.

### 타임라인 뷰 (뷰 전환 시)

시즌을 X축, 키워드를 Y축으로 — 각 셀에 시그널 강도를 히트맵으로 표시.

---

## DB 스키마

### 기존 테이블

```sql
runway_looks(
  id, designer, season, look_number,
  image_url, tags,  -- JSON array
  created_at
)

market_products(
  id, brand, name, price, category,
  color, material, size_info,
  image_url, product_url,
  crawled_at
)
```

### 신규 테이블

```sql
expert_reports(
  id INTEGER PRIMARY KEY,
  source TEXT NOT NULL,       -- 'wgsn','tagwalk','pantone','vogue','bof','highsnobiety','fashion_snoops'
  report_type TEXT,           -- 'seasonal_forecast','color_report','material_report','editorial_review'
  season TEXT,                -- '24SS'~'26FW'
  publish_date TEXT,
  file_path TEXT,
  processed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

expert_keywords(
  id INTEGER PRIMARY KEY,
  report_id INTEGER REFERENCES expert_reports(id),
  keyword TEXT NOT NULL,
  category TEXT,              -- 'color','material','silhouette','style','item'
  confidence TEXT DEFAULT 'medium',
  is_runway_match BOOLEAN,
  pool TEXT,                  -- 'A'/'B'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

keyword_signals(
  id INTEGER PRIMARY KEY,
  keyword TEXT NOT NULL,
  season TEXT NOT NULL,
  signal_type TEXT NOT NULL,  -- 'runway','expert','celeb','search','social','market','campaign'
  signal_strength REAL,
  first_detected TEXT,
  source_detail TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

keyword_origin(
  id INTEGER PRIMARY KEY,
  keyword TEXT NOT NULL,
  season TEXT NOT NULL,
  origin_type TEXT,           -- 'runway_led','capital_driven','viral_meme','market_organic','unknown'
  confidence REAL,
  first_signal_type TEXT,
  signal_sequence TEXT,       -- JSON array
  auto_classified BOOLEAN DEFAULT TRUE,
  manual_override TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

celeb_search_volume(
  id INTEGER PRIMARY KEY,
  person_name TEXT NOT NULL,
  tier TEXT,
  keyword TEXT NOT NULL,
  volume INTEGER,
  volume_change_pct REAL,
  is_spike BOOLEAN DEFAULT FALSE,
  measured_date TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

celeb_sightings(
  id INTEGER PRIMARY KEY,
  person_name TEXT NOT NULL,
  tier TEXT, keyword TEXT NOT NULL,
  image_url TEXT, source_url TEXT,
  sighting_date TEXT,
  manual_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

hot_item_log(
  id INTEGER PRIMARY KEY,
  season TEXT, category TEXT, style_keyword TEXT,
  evidence_type TEXT,
  evidence_detail TEXT,
  confidence TEXT DEFAULT 'medium',
  origin_type TEXT,
  reported_by TEXT,
  reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

keyword_evaluations(
  id INTEGER PRIMARY KEY,
  keyword TEXT, season TEXT, evaluator_name TEXT,
  evaluation TEXT,
  comment TEXT,
  evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

keyword_retrospectives(
  id INTEGER PRIMARY KEY,
  keyword TEXT, season TEXT,
  predicted_status TEXT, actual_status TEXT,
  origin_type TEXT, evaluator_name TEXT,
  retrospected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

vlm_labels(
  id INTEGER PRIMARY KEY,
  source_type TEXT, source_id INTEGER,
  item TEXT, shape TEXT, size TEXT, color TEXT, texture TEXT,
  raw_response TEXT, model_used TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## 동의어 매핑 사전

```python
SYNONYM_MAP = {
    "sheer": ["transparent", "see-through", "시스루"],
    "oversized": ["loose fit", "relaxed fit", "오버사이즈", "boxy"],
    "leather": ["가죽", "faux leather", "레더", "vegan leather"],
    "denim": ["데님", "jeans", "진"],
    "knit": ["knitwear", "니트", "knitted"],
    "burgundy": ["wine", "maroon", "버건디", "와인"],
    "tailoring": ["tailored", "suiting", "blazer", "테일러드"],
    "wool": ["울", "woolen", "cashmere"],
    "silk": ["실크", "satin", "새틴"],
    "crop": ["크롭", "cropped"],
    "wide": ["와이드", "wide leg"],
    "slim": ["슬림", "skinny", "스키니"],
}

COLOR_NAMES = {"black","white","navy","burgundy","beige","camel","khaki","red","blue","green","yellow","pink","purple","orange","gray","brown","cream","ivory","cobalt","cherry","olive","teal","coral","lavender","mint","sage"}

MATERIAL_NAMES = {"leather","denim","sheer","knit","wool","silk","linen","cotton","nylon","polyester","suede","velvet","satin","mesh","lace","tweed","corduroy","fleece","fur","faux fur"}

SILHOUETTE_NAMES = {"oversized","slim","wide","crop","maxi","mini","midi","structured","relaxed","fitted","boxy","flared","tapered","asymmetric","draped"}
```

## 런웨이 시즌 매핑

| 시즌 | 쇼 시기 | 리테일 시즌 |
|-----|--------|------------|
| 24SS | 2023.09~10 | 2024.02~07 |
| 24FW | 2024.02~03 | 2024.08~01 |
| 25SS | 2024.09~10 | 2025.02~07 |
| 25FW | 2025.02~03 | 2025.08~01 |
| 26SS | 2025.09~10 | 2026.02~07 |
| 26FW | 2026.02~03 | 2026.08~01 |

## Confidence 계산

```python
def calculate_confidence(runway, expert, celeb, search, market, evaluator_adj=0):
    weights = {"runway":0.25, "expert":0.20, "celeb":0.15, "search":0.20, "market":0.20}
    raw = runway*weights["runway"] + expert*weights["expert"] + celeb*weights["celeb"] + search*weights["search"] + market*weights["market"]
    return round(max(0, min(1, raw + evaluator_adj)) * 100)
```

## Origin 자동 분류

```python
def classify_origin(signals: list[dict]) -> dict:
    """signals = sorted by first_detected, each {type, strength}"""
    if not signals:
        return {"type": "unknown", "confidence": 0}
    first = signals[0]["type"]
    types = {s["type"] for s in signals}
    if first == "runway" and "expert" in types:
        return {"type": "runway_led", "confidence": 0.8}
    if "campaign" in types and first in ("campaign", "celeb"):
        return {"type": "capital_driven", "confidence": 0.7}
    if first == "social" and "runway" not in types:
        return {"type": "viral_meme", "confidence": 0.75}
    if first == "market" and "runway" not in types:
        return {"type": "market_organic", "confidence": 0.6}
    return {"type": "unknown", "confidence": 0.3}
```

## VLM 프롬프트

```
Analyze this fashion runway look image. Respond ONLY in JSON:
{
  "items": [{"item":"<bag|shoe|jacket|...>","shape":"<round|square|...>","size":"<mini|small|medium|large|oversized>","color":"<color>","texture":"<matte|glossy|...>"}],
  "overall_silhouette": "<oversized|slim|wide|fitted|...>",
  "dominant_colors": ["<color1>","<color2>"],
  "key_materials": ["<material1>","<material2>"]
}
```

## 파일 구조

```
ftib/
├── backend/
│   ├── api/
│   │   ├── main.py                  ← FastAPI 앱 + 라우터 등록
│   │   └── routes/
│   │       ├── brands.py
│   │       ├── products.py          ← 상품 API (keyword 필터 포함)
│   │       ├── runway.py            ← 런웨이 API (tag 필터 포함)
│   │       ├── trendflow.py         ← Trend Flow 원본 API
│   │       ├── trendflow_check.py   ← Trend Flow check API (VLM+마켓 실데이터)
│   │       ├── analysis.py          ← Trend Analysis + Graph View API
│   │       └── vlm.py              ← VLM Labels API
│   ├── crawlers/
│   │   ├── base_crawler.py          ← 크롤러 추상 베이스
│   │   ├── brand_configs.py         ← 브랜드 설정 레지스트리 (23+ 브랜드)
│   │   ├── platform_crawlers/
│   │   │   ├── cafe24.py            ← Cafe24 공통 (marithe, coor, youth, mardi, emis...)
│   │   │   └── shopify.py           ← Shopify 공통 (alo, lemaire, stussy, fila)
│   │   └── brand_crawlers/
│   │       ├── nike.py, northface.py, descente.py, kolonsport.py, newbalance.py
│   │       ├── zara.py              ← stealth + API 인터셉트
│   │       ├── hm.py                ← stealth + article 파싱
│   │       ├── lululemon.py, acne_studios.py, on_running.py
│   │       ├── ralph_lauren.py, thisisneverthat.py
│   │       ├── maison_kitsune.py, ami.py
│   │       └── nanamica.py          ← 일본 브랜드
│   └── db/
│       ├── database.py              ← DDL + SEED_DATA (48 브랜드 등록)
│       └── ftib.db                  ← SQLite DB (6,800+ 상품)
├── frontend/src/
│   ├── pages/
│   │   ├── Runway.jsx               ← 런웨이 (/runway, ?tag=&season= 필터)
│   │   ├── TrendFlow.jsx            ← 기존 Trend Flow (/flow)
│   │   ├── TrendFlowCheck.jsx       ← Trend Flow check(Test) (/flow-check)
│   │   ├── TrendAnalysis.jsx        ← Trend Analysis (/trend)
│   │   ├── GraphView.jsx            ← Graph View (/graph)
│   │   └── VlmViewer.jsx            ← VLM Labels (/vlm)
│   ├── components/
│   │   ├── ProductBoard.jsx          ← Market Brand Board (/, Trend Keywords 칩)
│   │   ├── ProductCard.jsx
│   │   ├── ProductDetail.jsx
│   │   ├── Sidebar.jsx               ← 조닝별 브랜드 하이어라키 + TBA
│   │   └── trendflow/
│   │       ├── FilterBar.jsx, CategoryTabs.jsx
│   │       ├── KeywordCard.jsx, KeywordGrid.jsx, KeywordDetailPanel.jsx
│   │       ├── SignalBar.jsx, TimelineBar.jsx
│   │       ├── MatrixView.jsx, TimelineView.jsx
│   │       └── mockData.js
│   ├── hooks/
│   │   ├── useProducts.js            ← useBrands, useProducts, useCategories, useTrendChips
│   │   └── useTrendFlowCheck.js      ← useTrendFlowKeywords, useTrendFlowKeywordDetail
│   ├── utils/formatPrice.js          ← KRW, USD, EUR, JPY 포맷
│   └── styles/index.css
├── scripts/
│   ├── run_crawl.py                  ← 크롤링 실행 + DB 저장
│   └── vlm_pilot.py                  ← VLM 라벨링 (Claude Vision Sonnet)
├── CLAUDE.md                         ← 이 파일
├── BRAND_CRAWL_LIST.md               ← 크롤링 대상 브랜드 관리
└── .env                              ← ANTHROPIC_API_KEY
```

## 카테고리 체계

```
의류 (Wear)                    용품 (Accessory)
├── outer (아우터)              ├── headwear (모자)
├── inner (상의)                ├── bag (가방)
├── bottom (하의)               ├── shoes (신발)
└── wear_etc (기타의류)          └── acc_etc (기타용품)
```

## 데이터 현황 (2026-03-18)

- **마켓 상품**: 6,812개 (23개 브랜드)
- **런웨이 룩**: 10,930개 (38 디자이너, 6시즌)
- **VLM 라벨**: 진행 중 (목표 10,930개)
- **관리 문서**: BRAND_CRAWL_LIST.md (수집 현황 + 우선순위)

## 크롤러 아키텍처

- **Cafe24**: config dict만 추가 (marithe, coor, youth, blankroom, mardi, emis, dunst)
- **Shopify**: config dict만 추가 (alo, lemaire, stussy, fila)
- **Custom (Playwright)**: 브랜드별 크롤러 파일 (nike, northface, descente, zara 등)
- **Stealth**: playwright-stealth로 WAF 우회 (Zara, H&M, On Running, Ralph Lauren)
- **API 인터셉트**: Zara — 페이지 로드 시 /category/{id}/products?ajax=true 캡처
- **Apollo GraphQL**: Kolon Sport — __NEXT_DATA__ apolloState 파싱

## 페이지 구조 (7 pages)

| 페이지 | 경로 | 설명 |
|--------|------|------|
| Trend Flow | /flow | 트렌드 전파 프레임워크 (Origin Flow, Zone, Timeline) |
| Trend Flow check(Test) | /flow-check | VLM+마켓 실데이터 4단계 drill-down |
| Runway | /runway | 런웨이 룩 (?tag=&season= 필터) |
| Runway(VLM Test) | /vlm | VLM 라벨 뷰어 |
| Market Brand Board | / | 마켓 상품 + Runway Trend Keywords 칩 필터 |
| Trend Analysis | /trend | 컬러/소재/실루엣 분석 |
| Graph View | /graph | 브랜드-소재-컬러 관계 그래프 |
