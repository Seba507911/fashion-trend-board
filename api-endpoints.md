# FTIB API 엔드포인트 명세

## Base URL
```
http://localhost:8000/api
```

---

## Brands

### GET /api/brands
브랜드 목록 조회.

**Query Params:**
- `type`: `own` | `competitor` | 생략(전체)

**Response:**
```json
[
  {
    "id": "mlb",
    "name": "MLB",
    "name_kr": "MLB",
    "brand_type": "own",
    "website_url": "https://www.mlb-korea.com",
    "product_count": 156,
    "latest_score": 78.5
  }
]
```

---

## Products

### GET /api/products
상품 목록 조회 (필터, 정렬, 페이지네이션).

**Query Params:**
- `brand_id`: 브랜드 필터 (복수: `brand_id=mlb&brand_id=nike`)
- `season_id`: 시즌 필터
- `category_id`: 카테고리 필터 (복수 가능)
- `parent_category`: 대분류 필터 (`apparel`, `accessories`, `footwear`)
- `price_min`, `price_max`: 가격 범위
- `style_tag`: 스타일 태그 필터
- `min_score`: 최소 스코어
- `sort`: `score_desc` | `score_asc` | `price_desc` | `price_asc` | `newest`
- `page`: 페이지 번호 (default: 1)
- `per_page`: 페이지 당 개수 (default: 24, max: 100)

**Response:**
```json
{
  "total": 342,
  "page": 1,
  "per_page": 24,
  "products": [
    {
      "id": "mlb_3AWSB0143",
      "brand_id": "mlb",
      "brand_name": "MLB",
      "season_id": "2025SS",
      "category_id": "hat",
      "category_name_kr": "모자",
      "product_name": "Classic Monogram Ball Cap",
      "product_name_kr": "클래식 모노그램 볼캡",
      "price": 49000,
      "sale_price": null,
      "colors": ["Black", "Navy", "White"],
      "materials": ["Cotton 100%"],
      "thumbnail_url": "https://...",
      "product_url": "https://...",
      "style_tags": ["classic", "logo"],
      "total_score": 87.5,
      "score_breakdown": {
        "search_buzz": 92,
        "market_presence": 78,
        "manual_signal": 85
      },
      "pipeline_stage": "PEAK"
    }
  ]
}
```

### GET /api/products/{id}
상품 상세 (시그널 시계열 포함).

### GET /api/brands/{brand_id}/products
특정 브랜드의 상품 목록. 같은 필터 파라미터 지원.

---

## Scores

### GET /api/scores
스코어 조회.

**Query Params:**
- `target_type`: `product` | `brand` | `category` | `style_tag` | `color`
- `target_id`: 특정 대상
- `season_id`: 시즌 필터
- `score_type`: `total` | `search_buzz` | `market_presence` | `manual_signal` | `gap`
- `min_score`: 최소 점수
- `sort`: `score_desc` | `score_asc`

### GET /api/scores/pivot
피벗 뷰용 매트릭스 데이터.

**Query Params:**
- `row_axis`: `brand` | `category` | `style_tag` (default: `brand`)
- `col_axis`: `category` | `brand` | `style_tag` (default: `category`)
- `season_id`: 시즌 필터
- `score_type`: 표시할 스코어 타입 (default: `total`)

**Response:**
```json
{
  "row_axis": "brand",
  "col_axis": "category",
  "rows": [
    {"id": "mlb", "name": "MLB"},
    {"id": "nike", "name": "Nike"}
  ],
  "columns": [
    {"id": "outer", "name_kr": "아우터"},
    {"id": "top", "name_kr": "상의"}
  ],
  "data": {
    "mlb": {
      "outer": {
        "product_count": 15,
        "avg_score": 72.3,
        "max_score": 94,
        "trend": "up",
        "week_change": 5.2
      }
    }
  },
  "season_id": "2025SS"
}
```

### GET /api/scores/top
카테고리별 / 브랜드별 Top N 아이템.

**Query Params:**
- `group_by`: `category` | `brand`
- `n`: Top N개 (default: 5)
- `season_id`: 시즌

---

## Compare

### GET /api/compare
브랜드 간 비교 데이터.

**Query Params:**
- `brand_a`: 자사 브랜드 ID
- `brand_b`: 경쟁 브랜드 ID
- `season_id`: 시즌
- `category_id`: 카테고리 (생략 시 전체)

**Response:**
```json
{
  "brand_a": {
    "id": "mlb",
    "name": "MLB",
    "categories": {
      "outer": {
        "count": 15,
        "avg_score": 72,
        "top_products": [...]
      }
    },
    "total_products": 156,
    "avg_total_score": 68.5
  },
  "brand_b": { ... },
  "gaps": [
    {
      "category": "bottom",
      "style_tag": "barrel-leg",
      "gap_score": 85,
      "description": "경쟁사 대비 배럴 핏 데님 부재, 검색량 급증 중"
    }
  ]
}
```

---

## Signals

### POST /api/signals/manual
수동 시그널 입력.

**Request Body:**
```json
{
  "target_type": "style_tag",
  "target_id": "barrel-leg",
  "signal_type": "manual",
  "signal_value": 85,
  "signal_date": "2025-03-06",
  "metadata": {
    "note": "밀라노 FW 런웨이 다수 등장",
    "source": "vogue_runway"
  }
}
```

---

## Predictions

### POST /api/predictions
예측 기록.

**Request Body:**
```json
{
  "target_type": "style_tag",
  "target_id": "barrel-leg",
  "season_id": "2025FW",
  "prediction_text": "배럴 레그 데님이 FW 시즌 데님 카테고리 Top 3에 진입할 것",
  "predicted_score": 88,
  "confidence": "high"
}
```

### PUT /api/predictions/{id}/verify
시즌 종료 후 예측 결과 기록.

**Request Body:**
```json
{
  "actual_score": 72,
  "accuracy_note": "Top 5에는 진입했지만 와이드 스트레이트에 밀림. 가격대가 높은 브랜드에서만 인기"
}
```

### GET /api/predictions
예측 목록. 검증 여부 필터 가능.

**Query Params:**
- `season_id`: 시즌
- `verified`: `true` | `false` | 생략(전체)

---

## Import / Crawl

### POST /api/import/csv
CSV 데이터 임포트.

**Request:** multipart/form-data
- `file`: CSV/Excel 파일
- `import_type`: `products` | `signals` | `predictions`
- `brand_id`: 브랜드 (products일 때)

### POST /api/crawl/{brand_id}
수동 크롤링 트리거.

**Query Params:**
- `season_id`: 시즌 (생략 시 현재 시즌)
- `dry_run`: `true` (DB 저장 없이 결과만 반환)

**Response:**
```json
{
  "brand_id": "mlb",
  "products_found": 45,
  "products_new": 12,
  "products_updated": 33,
  "errors": 0,
  "duration_seconds": 28.5
}
```
