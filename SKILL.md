# FTIB Project — Claude Code Skill

> Claude Code가 FTIB 프로젝트 작업 시 참조하는 프로젝트 컨텍스트.

## 프로젝트 개요

Fashion Trend Intelligence Board — 패션 트렌드 전파를 데이터 기반으로 추적하는 대시보드.
**핵심**: 트렌드가 어디에서 시작(Origin)되어 어떤 경로로 전파되는지를 정량적으로 추적.

## 기술 스택

- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite + Tailwind CSS
- **Database**: SQLite (Vercel 서버리스 호환)
- **배포**: GitHub + Vercel 자동 배포
- **크롤링**: Playwright (기본) + Hyperbrowser (WAF 우회, API키: `HYPERBROWSER_API_KEY`)
- **VLM**: Claude Vision Sonnet (1순위), Gemini Flash (대량 처리 대안)

## 핵심 개념

### Origin 4타입 — 각각이 다른 파이프라인

```
Runway-led:     런웨이 → 전문가 → 셀럽 → 검색 → 마켓   (순차적, 6~12M)
Capital-driven: 브랜드투자 → 캠페인 → 검색폭발 → 마켓   (런웨이/전문가 건너뜀)
Viral/Meme:     소셜밈 → 틱톡확산 → 검색급등 → 마켓소진  (모든 전통채널 우회)
Market-organic: 소비자수요 → 마켓점진확대 → 검색완만상승  (선행시그널 없음)
```

**Origin 자동 분류 = "어떤 시그널이 먼저 나타났는가"로 판별.**

### 패션 조닝별 Origin 지배 구조

| 조닝 | 지배 Origin | F&F 브랜드 | 딜레이 |
|------|-----------|-----------|--------|
| 럭셔리/하이엔드 | Runway-led 60% | Lemaire | 같은 시즌 |
| 스포츠/아웃도어 | Market-organic 40% | Nike, Descente, NorthFace | 1~2시즌 |
| 캐주얼/스트리트 | Viral 35% + Capital 30% | MLB, Youth, Marithe | 2~4개월 |
| SPA/매스 | 전체 팔로우 | Zara, 무신사 | 2~4개월 |

### 키워드 풀 A/B
- **풀 A**: 런웨이 Top 30 ∩ 전문가 리포트 (합의된 시그널)
- **풀 B**: 전문가 리포트 − 런웨이 (독립 예측)

### Confidence 지표
키워드별 4개 시그널(런웨이, 전문가, 검색량, 마켓) 종합 점수 (0~100%)

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
-- 전문가 리포트
expert_reports(
  id INTEGER PRIMARY KEY,
  source TEXT NOT NULL,       -- 'wgsn','tagwalk','edited','pantone','pv','vogue','bof','highsnobiety','fashion_snoops'
  report_type TEXT,           -- 'seasonal_forecast','color_report','material_report','market_intelligence','editorial_review'
  season TEXT,                -- '24SS','24FW','25SS','25FW','26SS','26FW'
  publish_date TEXT,
  file_path TEXT,
  processed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 전문가 키워드
expert_keywords(
  id INTEGER PRIMARY KEY,
  report_id INTEGER REFERENCES expert_reports(id),
  keyword TEXT NOT NULL,
  category TEXT,              -- 'color','material','silhouette','style','item'
  confidence TEXT DEFAULT 'medium',
  is_runway_match BOOLEAN,   -- 자동 계산
  pool TEXT,                  -- 'A'/'B' 자동 분류
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 셀럽 검색량
celeb_search_volume(
  id INTEGER PRIMARY KEY,
  person_name TEXT NOT NULL,
  tier TEXT,                  -- 'T1','T2','T3','T4'
  keyword TEXT NOT NULL,
  volume INTEGER,
  volume_change_pct REAL,
  is_spike BOOLEAN DEFAULT FALSE,
  measured_date TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 셀럽 착용 기록
celeb_sightings(
  id INTEGER PRIMARY KEY,
  person_name TEXT NOT NULL,
  tier TEXT,
  keyword TEXT NOT NULL,
  image_url TEXT,
  source_url TEXT,
  sighting_date TEXT,
  manual_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 핫 아이템 로그
hot_item_log(
  id INTEGER PRIMARY KEY,
  season TEXT,
  category TEXT,
  style_keyword TEXT,
  evidence_type TEXT,         -- 'ranking_data','sold_out','search_spike','buyer_feedback','field_observation'
  evidence_detail TEXT,
  confidence TEXT DEFAULT 'medium',
  origin_type TEXT,           -- 'runway_led','capital_driven','viral_meme','market_organic'
  reported_by TEXT,
  reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 키워드 시그널 타임라인 (Origin 자동 분류용)
keyword_signals(
  id INTEGER PRIMARY KEY,
  keyword TEXT NOT NULL,
  season TEXT NOT NULL,
  signal_type TEXT NOT NULL,  -- 'runway','expert','celeb','search','social','market','campaign'
  signal_strength REAL,       -- 0~1 정규화
  first_detected TEXT,        -- ISO date
  source_detail TEXT,         -- "WGSN report", "Tagwalk FW25" 등
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Origin 분류 결과
keyword_origin(
  id INTEGER PRIMARY KEY,
  keyword TEXT NOT NULL,
  season TEXT NOT NULL,
  origin_type TEXT,           -- 'runway_led','capital_driven','viral_meme','market_organic','unknown'
  confidence REAL,            -- 분류 신뢰도 0~1
  first_signal_type TEXT,     -- 가장 먼저 나타난 시그널
  first_signal_date TEXT,
  signal_sequence TEXT,       -- JSON: ["runway","expert","search","market"] 순서
  auto_classified BOOLEAN DEFAULT TRUE,
  manual_override TEXT,       -- 수동 보정 시
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 키워드 평가 (레벨 1)
keyword_evaluations(
  id INTEGER PRIMARY KEY,
  keyword TEXT, season TEXT, evaluator_name TEXT,
  evaluation TEXT,            -- 'agree','disagree'
  comment TEXT,
  evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 키워드 사후 검증 (레벨 2)
keyword_retrospectives(
  id INTEGER PRIMARY KEY,
  keyword TEXT, season TEXT,
  predicted_status TEXT,
  actual_status TEXT,
  origin_type TEXT,
  evaluator_name TEXT,
  retrospected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- VLM 라벨링
vlm_labels(
  id INTEGER PRIMARY KEY,
  source_type TEXT,           -- 'runway','market'
  source_id INTEGER,
  item TEXT, shape TEXT, size TEXT, color TEXT, texture TEXT,
  raw_response TEXT,
  model_used TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Origin 자동 분류 로직

```python
def classify_origin(keyword: str, signals: list[dict]) -> dict:
    """
    시그널 발생 순서로 Origin 자동 분류.
    signals = sorted list of {type, first_detected, strength}
    """
    if not signals:
        return {"type": "unknown", "confidence": 0}
    
    first = signals[0]["type"]
    types_present = {s["type"] for s in signals}
    sequence = [s["type"] for s in signals]
    
    # Runway-led: 런웨이가 가장 먼저
    if first == "runway" and "expert" in types_present:
        return {
            "type": "runway_led",
            "confidence": 0.8 if "market" in types_present else 0.5,
            "first_signal": first,
            "sequence": sequence
        }
    
    # Capital-driven: 캠페인 감지 + 런웨이 부재/약함
    if "campaign" in types_present and first in ("campaign", "celeb"):
        return {
            "type": "capital_driven",
            "confidence": 0.7,
            "first_signal": first,
            "sequence": sequence
        }
    
    # Viral/Meme: 소셜이 먼저 + 런웨이/전문가 부재
    if first == "social" and "runway" not in types_present:
        return {
            "type": "viral_meme",
            "confidence": 0.75,
            "first_signal": first,
            "sequence": sequence
        }
    
    # Market-organic: 마켓이 먼저 + 선행 시그널 부재
    if first == "market" and "runway" not in types_present and "social" not in types_present:
        return {
            "type": "market_organic",
            "confidence": 0.6,
            "first_signal": first,
            "sequence": sequence
        }
    
    return {"type": "unknown", "confidence": 0.3, "first_signal": first, "sequence": sequence}
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
    "linen": ["린넨", "리넨"],
    "crop": ["크롭", "cropped"],
    "wide": ["와이드", "wide leg"],
    "slim": ["슬림", "skinny", "스키니"],
}

COLOR_NAMES = {
    "black","white","navy","burgundy","beige","camel","khaki",
    "red","blue","green","yellow","pink","purple","orange",
    "gray","grey","brown","cream","ivory","cobalt","cherry",
    "olive","teal","coral","lavender","mint","sage",
}

MATERIAL_NAMES = {
    "leather","denim","sheer","knit","wool","silk","linen",
    "cotton","nylon","polyester","suede","velvet","satin",
    "mesh","lace","tweed","corduroy","fleece","fur","faux fur",
}

SILHOUETTE_NAMES = {
    "oversized","slim","wide","crop","maxi","mini","midi",
    "structured","relaxed","fitted","boxy","flared","tapered",
    "asymmetric","draped",
}
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

## 전문가 리포트 소스 코드

| source | 설명 | 티어 |
|--------|------|------|
| wgsn | WGSN 장기 트렌드 예측 | T1 |
| tagwalk | Tagwalk 런웨이 정량 분석 | T1 |
| edited | EDITED 마켓 인텔리전스 | T2 |
| pantone | Pantone Color Institute | T2 |
| pv | Première Vision 소재 | T2 |
| vogue | Vogue Runway / BoF | T3 |
| highsnobiety | Highsnobiety/Hypebeast | T3 |
| fashion_snoops | Fashion Snoops | T3 |
| google_trends | Google Trends | T3 |
| naver_datalab | 네이버 DataLab | T3 |

## 패션 조닝 코드

| zoning | 브랜드 예시 | 지배 Origin |
|--------|-----------|-----------|
| luxury | Lemaire | runway_led |
| sports | Nike, Descente, NorthFace, Kolon Sport | market_organic |
| casual | MLB, Youth, Marithe, Coor, Blankroom | viral_meme, capital_driven |
| spa | Zara, H&M, 무신사 | 전체 팔로우 |
| active | ALO Yoga, New Balance | market_organic, capital_driven |

## VLM 프롬프트

```
Analyze this fashion runway look image and classify the following attributes.
Respond ONLY in JSON format.

{
  "items": [
    {
      "item": "<bag|shoe|jacket|pants|skirt|dress|top|accessory|coat|hat|scarf>",
      "shape": "<round|square|structured|unstructured|asymmetric|geometric|organic>",
      "size": "<mini|small|medium|large|oversized>",
      "color": "<primary color name in English>",
      "texture": "<matte|glossy|textured|quilted|woven|smooth|distressed|embossed>"
    }
  ],
  "overall_silhouette": "<oversized|slim|wide|fitted|relaxed|structured|draped>",
  "dominant_colors": ["<color1>", "<color2>"],
  "key_materials": ["<material1>", "<material2>"]
}
```

## Confidence 계산

```python
def calculate_confidence(
    runway_score: float,      # 0~1
    expert_score: float,      # 0~1
    search_score: float,      # 0~1
    market_score: float,      # 0~1
    evaluator_adj: float = 0  # -0.2 ~ +0.2
) -> int:
    weights = {"runway":0.30, "expert":0.25, "search":0.20, "market":0.25}
    raw = sum(score * weights[k] for k, score in
              zip(weights.keys(), [runway_score, expert_score, search_score, market_score]))
    return round(max(0, min(1, raw + evaluator_adj)) * 100)
```

## 파일 구조

```
ftib/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── routers/
│   │   ├── runway.py
│   │   ├── market.py
│   │   ├── trendflow.py        ← Origin 기반 재설계
│   │   ├── analysis.py
│   │   └── graph.py
│   ├── models/schemas.py
│   └── utils/
│       ├── synonym_map.py
│       ├── keyword_classifier.py
│       ├── origin_classifier.py  ← 신규: Origin 자동 분류
│       └── confidence.py
├── frontend/src/
│   ├── pages/
│   │   ├── MarketBrandBoard.jsx
│   │   ├── Runway.jsx
│   │   ├── TrendFlow.jsx        ← Origin 기반 재설계
│   │   ├── TrendAnalysis.jsx
│   │   └── GraphView.jsx
│   └── components/trendflow/
│       ├── OriginFlowView.jsx    ← 신규: Origin별 시그널 플로우
│       ├── ZoneDistribution.jsx  ← 신규: 조닝별 Origin 분포
│       ├── TimelineComparison.jsx ← 신규: 통합 타임라인
│       ├── KeywordList.jsx
│       ├── KeywordDetailPanel.jsx
│       ├── ExpertReportInput.jsx
│       ├── CelebrityTracker.jsx
│       └── ManualCorrectionUI.jsx
├── scripts/
│   ├── crawlers/
│   ├── runway_crawl/
│   ├── vlm/
│   └── backtest/
└── data/ftib.db
```

## Trend Flow 탭 컴포넌트 구조

```
TrendFlow.jsx
├── 상단: 시즌 선택 + 조닝 필터
├── 탭 1: OriginFlowView — Origin별 활성/비활성 채널 시각화
│   ├── Runway-led 플로우 (모든 채널 활성, 순차)
│   ├── Capital-driven 플로우 (캠페인→검색→마켓, 런웨이/전문가 비활성)
│   ├── Viral/Meme 플로우 (소셜→검색→마켓, 전통채널 비활성)
│   └── Market-organic 플로우 (마켓→검색, 선행시그널 비활성)
├── 탭 2: ZoneDistribution — 조닝별 Origin 비율 바 + 모니터링 포인트
├── 탭 3: TimelineComparison — 4가지 Origin의 시그널 타이밍 비교 바 차트
└── 하단: KeywordList + KeywordDetailPanel
    ├── 키워드별 Confidence 바 + Origin 태그 + 조닝 태그
    ├── 선택 시 타임라인 (시즌별 시그널 발생 순서)
    ├── 시그널 강도 바
    ├── VLM 분석 결과 (있으면)
    └── 수기 보정 UI (동의/비동의/코멘트)
```
