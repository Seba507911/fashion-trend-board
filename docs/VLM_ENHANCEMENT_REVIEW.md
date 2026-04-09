# VLM 라벨링 고도화 검토

> 목적: 런웨이 룩에서 더 풍부한 속성을 추출하여 전문가 키워드 매칭 정확도 향상
> 현재 상태: ~2,000/10,930 룩 라벨링 완료 (기존 프롬프트)

---

## 현재 프롬프트 vs 고도화 프롬프트

### 현재 프롬프트 (아이템당 속성 5개)

```json
{
  "items": [
    {
      "item": "jacket",
      "shape": "structured",
      "size": "oversized",
      "color": "navy",
      "texture": "matte"
    }
  ],
  "overall_silhouette": "oversized",
  "dominant_colors": ["navy", "white"],
  "key_materials": ["wool", "cotton"]
}
```

**문제점:**
- 아이템당 속성이 5개뿐 → 실루엣, 소재, 디테일 정보 부족
- shape가 아이템 형태와 실루엣을 혼용
- key_materials가 전체 룩 기준 → 아이템별 소재 구분 불가
- 핏, 기장, 구조적 디테일 전혀 추출 안 함
- FTIB 키워드(wide leg, sculpted shoulder, cropped 등)와 직접 매칭 불가


### 고도화 프롬프트 (아이템당 속성 12~15개)

```
Analyze this fashion runway look image. For each visible clothing item 
and accessory, extract detailed attributes.

IMPORTANT: For material, identify what the fabric LOOKS LIKE visually, 
not the fiber content. Focus on visual material categories 
(e.g., "denim", "knit", "leather", "sheer chiffon", "lace", "satin", 
"tweed", "corduroy") rather than guessing fiber composition 
(don't guess "cotton" vs "polyester" — these are indistinguishable 
from photos).

Respond ONLY in JSON:

{
  "items": [
    {
      "item_type": "<coat|jacket|blazer|vest|shirt|blouse|t-shirt|
                     tank_top|sweater|cardigan|hoodie|dress|skirt|
                     pants|shorts|jumpsuit|bag|shoe|hat|scarf|
                     belt|jewelry|other>",
      "item_subtype": "<specific name, e.g., trench_coat, bomber_jacket, 
                        cargo_pants, polo_shirt, pencil_skirt>",
      
      "color_primary": "<main color name>",
      "color_secondary": "<secondary color if present, else null>",
      "color_tone": "<light|medium|dark|vivid|muted|pastel|neon>",
      
      "visual_material": "<what the fabric looks like: denim, leather, 
                           suede, knit, jersey, lace, sheer_chiffon, 
                           sheer_organza, satin, silk_like, velvet, 
                           corduroy, tweed, mesh, canvas, poplin, 
                           technical_fabric, quilted, fur, faux_fur, 
                           woven_matte, woven_sheen, crochet>",
      "surface_finish": "<matte|semi_matte|subtle_sheen|glossy|
                          high_shine|distressed|washed|raw|polished|
                          crinkled|hammered|embossed>",
      "opacity": "<opaque|semi_sheer|sheer|transparent>",
      "weight_appearance": "<lightweight|medium|heavyweight>",
      "drape": "<stiff|structured|semi_structured|fluid|flowing>",
      
      "fit": "<skin_tight|slim|regular|relaxed|loose|oversized>",
      "length": "<cropped|short|regular|long|maxi|floor_length>",
      
      "notable_details": ["<up to 3 key construction or design details, 
                            e.g., padded_shoulders, wide_lapel, 
                            patch_pockets, side_slit, ruffle_hem, 
                            drawstring_waist, zip_closure, 
                            button_front, belt_detail, cutout, 
                            fringe, pleated, tiered, wrap_style>"]
    }
  ],
  
  "overall_silhouette": "<oversized|slim|wide|fitted|relaxed|
                          structured|draped|layered|columnar>",
  "silhouette_details": {
    "shoulder": "<natural|padded|sculpted|dropped|exaggerated>",
    "waist": "<undefined|natural|cinched|high|low|belted>",
    "hem_volume": "<straight|flared|bubble|balloon|tapered>"
  },
  
  "dominant_colors": ["<color1>", "<color2>"],
  "color_palette_mood": "<monochrome|tonal|contrasting|pastel|
                          earthy|bold|neutral|dark>",
  
  "pattern": "<solid|striped|plaid|polka_dot|floral|geometric|
               abstract|animal_print|camouflage|graphic|
               color_block|tie_dye|paisley|none>",
  
  "style_mood": ["<up to 2 mood tags: minimalist, romantic, sporty, 
                   utility, preppy, bohemian, tailored, streetwear, 
                   resort, grunge, retro, futuristic, feminine, 
                   masculine, androgynous, luxe, casual>"]
}
```

---

## VLM이 사진에서 구분할 수 있는 것 vs 없는 것

### ✅ 높은 신뢰도 (80%+)

| 속성 | 예시 | FTIB 키워드 매칭 |
|------|------|-----------------|
| 아이템 타입/서브타입 | trench_coat, cargo_pants | item 카테고리 직접 매칭 |
| 컬러 (기본) | navy, burgundy, white | color 직접 매칭 |
| 시각적 소재 카테고리 | leather, denim, knit, lace, sheer | material 직접 매칭 |
| 핏/실루엣 | oversized, slim, wide | silhouette 직접 매칭 |
| 기장 | cropped, maxi | silhouette 보조 |
| 투명도 | sheer, opaque | sheer 키워드 매칭 |
| 패턴 | floral, striped, polka_dot | print 매칭 |
| 어깨 구조 | padded, sculpted, dropped | sculpted_shoulder 매칭 |

### ⚠️ 중간 신뢰도 (50~70%)

| 속성 | 한계 | 대처 |
|------|------|------|
| satin vs silk-like | 구분 어려움 | "silk_like" 통합 |
| lightweight vs medium weight | 사진 각도 의존 | 드레이프로 보완 |
| suede vs nubuck | 매우 유사 | "suede" 통합 |
| 세부 디테일 (지퍼 등) | 사진 해상도 의존 | notable_details는 보이는 것만 |

### ❌ 불가능 (시도하지 말 것)

| 속성 | 이유 |
|------|------|
| cotton vs polyester | 시각적으로 동일 |
| organic cotton vs regular cotton | 불가능 |
| real leather vs faux leather | 대부분 구분 불가 |
| merino wool vs regular wool | 불가능 |
| 섬유 혼용률 (cotton 60% / poly 40%) | 불가능 |
| 원단 중량 (gsm) | 불가능 |

---

## FTIB 키워드 매칭 개선 효과

### 현재 매칭 가능 키워드

```
현재 VLM → FTIB 매칭 가능:
  컬러: ✅ (기본 컬러명)
  소재: △ (key_materials에 추측 포함, 신뢰도 낮음)
  실루엣: △ (overall_silhouette 1개만)
  아이템: ✅ (기본 타입)
  디테일: ❌
```

### 고도화 후 매칭 가능 키워드

```
고도화 VLM → FTIB 매칭 가능:
  컬러: ✅✅ (primary + secondary + tone)
  소재: ✅ (시각적 소재 카테고리 — 신뢰도 높은 것만)
  실루엣: ✅✅ (fit + shoulder + waist + hem_volume + length)
  아이템: ✅✅ (type + subtype)
  디테일: ✅ (notable_details)
  스타일: ✅ (style_mood — 매크로 테마 매칭용)
  패턴: ✅ (신규 — floral, stripe, polka_dot 등)
```

### 구체적 매칭 예시

```
WGSN 키워드: "Sculpted Shoulder" (14개 소스, Tier 2)
  현재 VLM: 매칭 불가 (shoulder 정보 없음)
  고도화 VLM: silhouette_details.shoulder = "sculpted" → 직접 매칭 ✅

WGSN 키워드: "Wide Leg" (22개 소스, Tier 1)
  현재 VLM: overall_silhouette = "wide" (룩 전체 기준, 부정확)
  고도화 VLM: pants.fit = "wide" + item_subtype = "wide_leg_pants" → 정확 매칭 ✅

WGSN 키워드: "Sheer" (11개 소스, Tier 1)
  현재 VLM: texture = "transparent" (가끔 잡힘)
  고도화 VLM: visual_material = "sheer_chiffon" + opacity = "sheer" → 확실 매칭 ✅

WGSN 키워드: "Barrel Leg" (12개 소스, Tier 2)
  현재 VLM: 매칭 불가
  고도화 VLM: silhouette_details.hem_volume = "balloon" + fit = "wide" → 매칭 가능 ✅

WGSN 키워드: "Lace" (11개 소스, Tier 1)
  현재 VLM: texture에 가끔 등장
  고도화 VLM: visual_material = "lace" → 직접 매칭 ✅
```

---

## 모델 비교: Claude Sonnet vs Gemini Flash

### Claude Sonnet (claude-sonnet-4-20250514)

| 항목 | 값 |
|------|-----|
| 이미지 인식 품질 | 높음 — 패션 디테일 식별 우수 |
| JSON 구조 준수 | 매우 높음 — 스키마 일탈 드묾 |
| 비용 (이미지 1장) | ~$0.008 (입력 이미지 + 출력 토큰) |
| 10,930장 전체 비용 | ~$87 |
| 속도 | 중간 (Rate limit 고려 시 ~4시간) |
| 고도화 프롬프트 적합성 | ✅ 복잡한 스키마도 안정적 |

### Gemini 2.0 Flash

| 항목 | 값 |
|------|-----|
| 이미지 인식 품질 | 중상 — 기본 속성은 정확, 세부 디테일은 Sonnet보다 약간 낮음 |
| JSON 구조 준수 | 중상 — 가끔 스키마 일탈 (null 처리, 배열 형식 등) |
| 비용 (이미지 1장) | ~$0.001 (Sonnet의 ~1/8) |
| 10,930장 전체 비용 | ~$11 |
| 속도 | 빠름 (높은 Rate limit) |
| 고도화 프롬프트 적합성 | ⚠️ 속성 수가 많아지면 누락 가능성 있음 |

### 추천 전략

```
Phase 1: Claude Sonnet으로 500장 파일럿
  → 고도화 프롬프트 품질 검증
  → 비용: ~$4

Phase 2a: 품질 OK → Claude Sonnet으로 전체 (나머지 10,430장)
  → 비용: ~$83, 시간: ~4시간
  → 총 비용: ~$87

Phase 2b: 비용 절감 필요 시 → Gemini Flash로 전체
  → Sonnet 500장 결과를 Ground Truth로 Gemini 품질 비교
  → 비용: ~$11, 시간: ~1시간
  → 품질 차이가 크면 Sonnet 유지
```

---

## DB 스키마 영향

### 현재 vlm_labels 테이블

```sql
vlm_labels(
  id, source_type, source_id,
  item, shape, size, color, texture,  -- 속성 5개
  raw_response, model_used, created_at
)
```

### 고도화 후 필요한 변경

**옵션 A: raw_response 활용 (스키마 변경 최소화)**
- 고도화된 JSON 전체를 raw_response에 저장
- 쿼리 시 JSON 파싱으로 속성 접근
- 장점: 스키마 변경 없음, 유연함
- 단점: 쿼리 성능 (SQLite JSON 함수 제한적)

**옵션 B: 컬럼 확장 (검색 성능 우선)**
```sql
vlm_labels_v2(
  id, source_type, source_id,
  -- 아이템 기본
  item_type, item_subtype,
  -- 컬러
  color_primary, color_secondary, color_tone,
  -- 소재/질감
  visual_material, surface_finish, opacity, weight_appearance, drape,
  -- 핏/실루엣
  fit, length,
  -- 디테일
  notable_details,  -- JSON array
  -- 룩 전체
  overall_silhouette, shoulder, waist, hem_volume,
  color_palette_mood, pattern, style_mood,
  -- 메타
  raw_response, model_used, created_at
)
```

**추천: 옵션 A (raw_response)로 시작, 매칭 쿼리 빈번해지면 옵션 B로 마이그레이션**

---

## 실행 계획

### 즉시 가능
1. 고도화 프롬프트로 샘플 10장 테스트 (이 대화에서 바로 가능)
2. Claude Sonnet / Gemini Flash 품질 비교

### 다음 단계
3. 500장 파일럿 → 품질 확인
4. 전체 10,930장 라벨링 (고도화 프롬프트)
5. Expert Review 페이지에서 "런웨이 VLM 매칭 수" 연동

---

## 핵심 정리

| 질문 | 답 |
|------|-----|
| 코튼 vs 폴리에스터 구분? | ❌ 불가능 — 시도하지 말 것 |
| 데님 vs 니트 vs 레더 구분? | ✅ 높은 신뢰도로 가능 |
| 실루엣 디테일 (어깨, 허리, 기장)? | ✅ 가능 — 현재 안 뽑고 있을 뿐 |
| 패턴 (플로럴, 스트라이프)? | ✅ 가능 — 현재 안 뽑고 있을 뿐 |
| 스타일 무드 (프레피, 리조트)? | ⚠️ 중간 — 주관적이지만 참고 가능 |
| 현재 모델로 가능? | ✅ 프롬프트 변경만으로 대폭 개선 |
| Gemini 대안? | ✅ 비용 1/8, 품질은 약간 낮음 |
