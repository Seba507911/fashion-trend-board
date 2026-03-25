# FTIB Expert Report Analysis Plan

> 전문가 리포트(WGSN 등)에서 디자이너별 핵심 인사이트를 추출하는 분석 전략.
> 단순 키워드 빈도가 아닌, **디자이너의 의도 + 업계 맥락 + 교차 근거**를 정리하는 것이 목표.

---

## 1. 목표 재정의

### ❌ 기존 접근 (키워드 빈도 추출)
```
"burgundy" → 12회 등장 → Confidence +0.2
```

### ✅ 새로운 접근 (디자이너 의도 해석)
```
Lemaire 26SS:
- structured tailoring으로 회귀 → WGSN #SmartenUp과 수렴
- brown leather를 악세서리 전반에 적용 → Enriched Classics 연장선
- oversized 실루엣 의도적 축소 → 시장 반응 반영 가능성

근거: WGSN Paris Men's S/S 26 리포트 #SepiaTones 컬러 방향
      + Hermès, Saint Laurent도 동일 방향 → 개별 취향이 아닌 방향성
```

### 궁극적 분석 단위
| 분석 축 | 예시 |
|---------|------|
| 디자이너 의도 | "왜 black이 아니라 brown을 선택했는가" |
| 소재/컬러 선택의 맥락 | "leather 악세서리가 utility인가, luxury인가" |
| 업계 예측과의 수렴/발산 | "WGSN 예측과 일치하는가, 독립적인가" |
| 디자이너 간 교차 패턴 | "같은 시즌에 같은 방향을 택한 디자이너들" |
| 시즌 간 변화 추적 | "24FW → 25SS → 25FW 방향 전환 여부" |

---

## 2. 데이터 소스 구분

### 2-1. 전문가 리포트 (WGSN 등) — ~300개/시즌
| 리포트 타입 | 역할 | 예시 |
|------------|------|------|
| Big Ideas / STEPIC | 거시 트렌드 프레임워크 | Big Ideas 2026: Fashion |
| Catwalk City Analytics | 도시별 런웨이 정량 분석 | NY Women's S/S 26, Paris Men's S/S 26 |
| Core Item Update | 아이템별 상세 디자인 전략 | Men's Jackets & Outerwear S/S 26 |
| Colour/Material Forecast | 컬러·소재 예측 | Men's Colour Forecast S/S 26 |
| Buying Director's Briefing | 바잉 전략 | Women's Key Items S/S 26 |
| Buyers' Debrief | 시즌 사후 분석 | Womenswear S/S 25 |

### 2-2. 런웨이 데이터 (이미 보유)
- 10,930 룩, 38 디자이너, 6시즌
- VLM 라벨링 진행 중 → 룩별 item/color/material/silhouette

### 2-3. 추가 수집 필요 (향후)
- Vogue Runway 디자이너 리뷰 / 쇼 노트
- BoF, Highsnobiety 에디토리얼
- 디자이너 인터뷰 (의도 파악 핵심)

---

## 3. 분석 3-레이어 프레임워크

```
Layer 1: 디자이너별 컬렉션 의도 파악
         ├── 쇼 노트 / 인터뷰 / 리뷰 → "뭘 말하려 했는가"
         └── VLM 룩 데이터 → "실제로 뭘 보여줬는가" (증거)

Layer 2: 전문가 리포트로 맥락 부여
         ├── WGSN 예측과 수렴하는가?
         ├── 어떤 STEPIC 트렌드와 연결되는가?
         └── 마켓 데이터가 뒷받침하는가?

Layer 3: 디자이너 간 교차 비교
         ├── 같은 시즌 내 패턴 (동시적 수렴)
         ├── 시즌 간 전파 추적 (시차적 확산)
         └── 조닝별 반응 차이 (luxury vs casual vs SPA)
```

---

## 4. 도구별 역할 분담

### 4-1. Claude API 배치 (Sonnet) — 1단계: 구조화된 해석 요약
**목적**: 300개 리포트를 각각 "해석이 담긴 중간 요약"으로 변환
**비용 추정**: 리포트당 ~$0.10 → 300개 = ~$30
**산출물**: JSON → `docs/report_summaries/` 폴더에 저장

```
입력: PDF 원본
출력: 리포트별 structured interpretation JSON
```

### 4-2. NotebookLM — 2단계: 교차 탐색
**목적**: 여러 리포트 간 패턴 발견, 탐색적 질문
**구성**: 시즌 × 도시/카테고리별 프로젝트 (5~8개)

| 프로젝트 | 소스 구성 | 핵심 질문 예시 |
|---------|---------|-------------|
| 26SS Paris Men's | WGSN Catwalk + Core Items + Colour + 주요 디자이너 리뷰 | "brown을 쓴 디자이너들의 공통 맥락은?" |
| 26SS NY Women's | WGSN Catwalk + Key Items + Buying Brief | "#2010Revival을 채택한 브랜드와 안 한 브랜드의 차이?" |
| 26SS Big Picture | Big Ideas + STEPIC + Forecast summaries | "가장 강한 cross-city 수렴 방향은?" |

### 4-3. Opus 채팅 (여기) — 3단계: 전략 해석
**목적**: 발견된 패턴을 FTIB 프레임워크에 적용
- Origin 분류 관점에서의 해석
- Confidence 계산에 어떻게 반영할지
- expert_keywords, keyword_signals 테이블 입력값 결정
- 최종 인사이트를 md로 정리 → Claude Code + 옵시디언 연동

### 4-4. Claude Code (Sonnet) — 코딩 실행
**목적**: 파이프라인 코드 작성, DB 작업, 프론트엔드
- `scripts/expert_report_pipeline.py` 작성
- DB 스키마 확장 (필요시)
- Trend Flow UI에 전문가 시그널 반영

---

## 5. 1단계 프롬프트 설계: 리포트 해석 요약

### 5-1. 프롬프트 전략

단순 키워드 추출이 아닌, **3가지 축의 해석**을 요구:

1. **리포트의 핵심 주장** (What does this report argue?)
2. **디자이너별 의도와 선택** (What did each designer choose and why?)
3. **교차 연결 가능한 맥락** (How does this connect to broader narratives?)

### 5-2. 시스템 프롬프트

```
You are a fashion industry analyst working for FTIB (Fashion Trend Intelligence Board).
Your task is to extract structured interpretive summaries from professional fashion 
forecast reports (WGSN, Tagwalk, etc.).

CRITICAL: Do NOT just list keywords. Extract the INTENT and CONTEXT behind each 
trend direction and designer choice.

You understand these FTIB concepts:
- Origin types: runway_led, capital_driven, viral_meme, market_organic
- Fashion zonings: luxury, sports, casual, spa, active
- Signal types: runway, expert, celeb, search, social, market, campaign
- Categories: color, material, silhouette, item, style
```

### 5-3. 리포트 타입별 추출 프롬프트

#### A) Catwalk City Analytics (도시별 런웨이 분석)

```
Analyze this catwalk analytics report and extract:

1. SEASON_OVERVIEW:
   - season, city, gender (e.g., "26SS", "Paris", "Men's")
   - core_thesis: The report's central argument in 1-2 sentences
   - market_context: Economic/cultural factors mentioned

2. DESIGNER_INSIGHTS (for each designer mentioned):
   - designer: name
   - intent: What was this designer trying to communicate?
   - key_choices: Specific items, colors, materials, silhouettes chosen
   - choice_rationale: Why these choices matter (based on report context)
   - wgsn_alignment: Which WGSN themes/hashtags does this align with?
   - deviation: Anything that goes AGAINST the mainstream direction?

3. TREND_DIRECTIONS (for each identified direction):
   - direction_name: (e.g., "#SmartenUp", "#SoftUtility")
   - description: What this direction means in practice
   - supporting_designers: Which designers exemplify this?
   - evidence_type: "quantitative" (ppt change, % mix) or "qualitative" (styling, narrative)
   - quantitative_data: Any specific numbers (e.g., "+2.9ppt YoY for black")
   - commercial_implication: What should brands DO with this information?

4. COLOR_SIGNALS:
   - rising: [{color, change, context}]
   - declining: [{color, change, context}]
   - emerging: [{color, context, which_designers}]

5. MATERIAL_SIGNALS:
   - key_materials: [{material, context, designers}]
   - surface_treatments: [{treatment, context}]

6. SILHOUETTE_SIGNALS:
   - dominant_fits: [{silhouette, context, evolution_from_last_season}]
   - emerging_fits: [{silhouette, context, which_designers}]

7. CROSS_REPORT_CONNECTIONS:
   - References to other WGSN reports or forecasts mentioned
   - Connections to Big Ideas / STEPIC themes
   - Potential links to other cities/seasons

Respond ONLY in JSON format.
```

#### B) Big Ideas / STEPIC (거시 트렌드)

```
Analyze this macro trend report and extract:

1. FRAMEWORK_OVERVIEW:
   - report_title, publish_date, forecast_horizon
   - methodology: STEPIC categories covered
   
2. TREND_THEMES (for each major theme):
   - theme_name: (e.g., "Design for Need", "Feel Appeal")
   - stepic_category: Society/Technology/Environment/Politics/Industry/Creativity
   - driver: underlying force
   - innovations: specific innovation directions
   - core_argument: 2-3 sentence summary
   - fashion_strategy: What the report recommends for fashion brands
   - actionable_keywords: Specific design/product directions mentioned
   - brand_examples: [{brand, action, relevance}]

3. FASHION_IMPLICATIONS:
   - For each FTIB zoning (luxury, sports, casual, spa):
     - relevant_themes: Which Big Ideas apply most?
     - expected_impact: How might this change product direction?
     - timeline: When will this hit retail?

4. KEYWORD_EXTRACTION (secondary):
   - colors mentioned with context
   - materials mentioned with context  
   - silhouettes mentioned with context
   - items mentioned with context
   - Each with: {keyword, category, context_sentence, confidence: high/medium/low}

Respond ONLY in JSON format.
```

#### C) Core Item Update (아이템별 전략)

```
Analyze this core item report and extract:

1. ITEM_OVERVIEW:
   - item_category, season, gender
   - market_status: TrendCurve classification (Rising/Flat/Declining)
   - core_opportunity: Main commercial argument

2. ITEM_VARIANTS (for each variant):
   - variant_name: (e.g., "The classic Harrington", "The sporty track jacket")
   - design_strategy: Key design directions
   - color_direction: Recommended colors with rationale
   - material_direction: Recommended materials/textures
   - detail_direction: Key details (pockets, zips, trims)
   - theme_alignment: Which WGSN themes this serves
   - target_market: Who is this for?
   - brand_examples: [{brand, specific_product, relevance}]

3. TREND_CURVE_DATA:
   - uk_status, us_status
   - timing_recommendation: When to launch/markdown
   - buy_depth_guidance: Investment level suggested

Respond ONLY in JSON format.
```

---

## 6. 산출물 파일 구조

```
ftib/
├── docs/
│   ├── EXPERT_ANALYSIS_PLAN.md        ← 이 파일
│   ├── PROGRESS_LOG.md                ← 진행 상황 추적
│   ├── report_summaries/              ← 1단계 산출물
│   │   ├── 26ss/
│   │   │   ├── paris_mens_catwalk.json
│   │   │   ├── ny_womens_catwalk.json
│   │   │   ├── big_ideas_2026.json
│   │   │   └── core_items_mens_jackets.json
│   │   ├── 25fw/
│   │   └── 25ss/
│   ├── designer_profiles/             ← 디자이너별 종합 해석
│   │   ├── lemaire.md
│   │   ├── sacai.md
│   │   └── wales_bonner.md
│   └── season_insights/               ← 시즌별 교차 분석 결과
│       ├── 26ss_color_convergence.md
│       ├── 26ss_silhouette_shifts.md
│       └── 26ss_origin_signals.md
```

---

## 7. DB 스키마 확장 제안

기존 `expert_reports` + `expert_keywords` 테이블에 추가:

```sql
-- 디자이너별 시즌 인사이트 (Layer 1)
designer_season_insights(
  id INTEGER PRIMARY KEY,
  designer TEXT NOT NULL,
  season TEXT NOT NULL,
  collection_intent TEXT,           -- 컬렉션 의도 요약
  key_choices TEXT,                 -- JSON: [{type, choice, rationale}]
  wgsn_alignment TEXT,              -- JSON: ["#SmartenUp", "#SoftUtility"]
  deviation_notes TEXT,             -- 주류 방향과 다른 점
  source_reports TEXT,              -- JSON: [report_id, ...]
  confidence TEXT DEFAULT 'medium',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 교차 패턴 기록 (Layer 3)  
cross_pattern_log(
  id INTEGER PRIMARY KEY,
  season TEXT NOT NULL,
  pattern_name TEXT NOT NULL,       -- e.g., "brown_convergence_26ss"
  pattern_type TEXT,                -- 'color_convergence', 'silhouette_shift', 'item_emergence'
  description TEXT,
  supporting_designers TEXT,        -- JSON: ["Hermès", "Saint Laurent", "Sacai"]
  supporting_reports TEXT,          -- JSON: [report_id, ...]
  origin_implication TEXT,          -- Origin 분류에 대한 함의
  confidence TEXT DEFAULT 'medium',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## 8. 실행 순서 (Action Items)

### Phase 1: 파이프라인 구축 (Claude Code)
- [ ] `scripts/expert_report_pipeline.py` 작성
  - PDF → base64 → Claude API (Sonnet) → JSON
  - 리포트 타입 자동 감지 → 적절한 프롬프트 선택
  - 결과를 `docs/report_summaries/` + DB에 저장
- [ ] DB 스키마 확장 (designer_season_insights, cross_pattern_log)
- [ ] 파일럿 테스트: 업로드된 4개 리포트로 검증

### Phase 2: 배치 처리
- [ ] WGSN 리포트 정리 (시즌별 폴더 구조)
- [ ] 배치 실행 (300개 리포트 → JSON 요약)
- [ ] 추출 품질 검증 (Opus에서 샘플 리뷰)

### Phase 3: 교차 분석 (NotebookLM + Opus)
- [ ] NotebookLM 프로젝트 구성 (시즌별 5~8개)
- [ ] 탐색적 분석 → 패턴 발견
- [ ] Opus에서 패턴 해석 → FTIB 프레임워크 적용
- [ ] designer_profiles/ 작성

### Phase 4: FTIB 통합
- [ ] expert_keywords 테이블에 해석 기반 데이터 입력
- [ ] keyword_signals에 전문가 시그널 반영
- [ ] Trend Flow UI에 전문가 레이어 추가

---

## 9. 파일럿 테스트: 업로드된 4개 리포트

오늘 업로드된 리포트로 즉시 파일럿 가능:

| 파일 | 타입 | 프롬프트 |
|-----|------|---------|
| Big_Ideas_2026__Fashion_en.pdf | Big Ideas / STEPIC | 프롬프트 B |
| Catwalk_City_Analytics__New_York_Women_s_S_S_26_en.pdf | Catwalk Analytics | 프롬프트 A |
| Catwalk_City_Analytics__Paris_Men_s_S_S_26_en.pdf | Catwalk Analytics | 프롬프트 A |
| Core_Item_Update__Men_s_Jackets___Outerwear_S_S_26_en.pdf | Core Item | 프롬프트 C |

→ Claude Code에서 파이프라인 코드 작성 후, 이 4개로 먼저 테스트

---

## 10. 환경별 작업 가이드

| 환경 | 모델 | 용도 | 언제 쓸까 |
|-----|------|------|---------|
| **프로젝트 채팅 (여기)** | Opus | 전략 논의, 해석, md 정리 | 방향 결정, 인사이트 해석, 문서화 |
| **Claude Code** | Sonnet | 코딩, DB, 파이프라인 | 스크립트 작성, UI 작업, 배치 실행 |
| **NotebookLM** | Gemini | 교차 탐색, 패턴 발견 | 여러 리포트 비교, 탐색적 질문 |
| **Claude API (배치)** | Sonnet | 대량 처리 | 300개 리포트 → JSON 변환 |

### 연결 고리: 모든 산출물은 md/json 파일로 → Git 커밋 → 옵시디언에서 열람

---

*마지막 업데이트: 2026-03-23*
*논의 환경: Opus 프로젝트 채팅*
