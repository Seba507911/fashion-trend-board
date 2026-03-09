# FTIB Database Schema Detail

## 목차
1. [brands](#brands)
2. [seasons](#seasons)
3. [categories](#categories)
4. [products](#products)
5. [signals](#signals)
6. [scores](#scores)
7. [predictions](#predictions)
8. [인덱스 전략](#인덱스)
9. [마이그레이션 노트](#마이그레이션)

---

## brands

브랜드 마스터 테이블. 자사(own)와 경쟁(competitor) 구분.

```sql
CREATE TABLE brands (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    name_kr     TEXT,
    brand_type  TEXT NOT NULL CHECK(brand_type IN ('own', 'competitor')),
    logo_url    TEXT,
    website_url TEXT,
    crawl_config TEXT,               -- JSON: 크롤러 설정
    is_active   INTEGER DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**시드 데이터 예시:**
```sql
INSERT INTO brands (id, name, name_kr, brand_type, website_url) VALUES
('mlb', 'MLB', 'MLB', 'own', 'https://www.mlb-korea.com'),
('discovery', 'Discovery Expedition', '디스커버리 익스페디션', 'own', 'https://www.discovery-expedition.com'),
('duvetica', 'Duvetica', '듀베티카', 'own', NULL);
```

---

## seasons

시즌 마스터. 패션 산업 표준 시즌 코드 사용.

```sql
CREATE TABLE seasons (
    id          TEXT PRIMARY KEY,
    year        INTEGER NOT NULL,
    season_code TEXT NOT NULL CHECK(season_code IN ('SS', 'FW', 'RS', 'PF', 'CR')),
    label       TEXT,                -- '2025 Spring/Summer'
    start_date  DATE,
    end_date    DATE,
    is_current  INTEGER DEFAULT 0
);
```

**시즌 코드:**
- `SS`: Spring/Summer
- `FW`: Fall/Winter
- `RS`: Resort (Cruise)
- `PF`: Pre-Fall
- `CR`: Cruise

---

## categories

계층형 카테고리. parent_id로 대분류(의류/용품) → 중분류(아우터/상의 등) 표현.

```sql
CREATE TABLE categories (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    name_kr     TEXT NOT NULL,
    parent_id   TEXT REFERENCES categories(id),
    sort_order  INTEGER DEFAULT 0,
    icon        TEXT                 -- emoji 또는 아이콘 코드
);
```

**시드 데이터:**
```sql
-- 대분류
INSERT INTO categories (id, name, name_kr, parent_id, sort_order) VALUES
('apparel', 'Apparel', '의류', NULL, 1),
('accessories', 'Accessories', '용품', NULL, 2),
('footwear', 'Footwear', '신발', NULL, 3);

-- 의류 하위
INSERT INTO categories (id, name, name_kr, parent_id, sort_order) VALUES
('outer', 'Outer', '아우터', 'apparel', 1),
('top', 'Top', '상의', 'apparel', 2),
('bottom', 'Bottom', '하의', 'apparel', 3),
('dress', 'Dress', '원피스', 'apparel', 4),
('set', 'Set-up', '셋업', 'apparel', 5);

-- 용품 하위
INSERT INTO categories (id, name, name_kr, parent_id, sort_order) VALUES
('bag', 'Bag', '가방', 'accessories', 1),
('hat', 'Hat/Cap', '모자', 'accessories', 2),
('scarf', 'Scarf/Muffler', '스카프/머플러', 'accessories', 3),
('jewelry', 'Jewelry', '주얼리', 'accessories', 4),
('etc_acc', 'Others', '기타용품', 'accessories', 5);

-- 신발 하위
INSERT INTO categories (id, name, name_kr, parent_id, sort_order) VALUES
('sneakers', 'Sneakers', '스니커즈', 'footwear', 1),
('boots', 'Boots', '부츠', 'footwear', 2),
('sandals', 'Sandals', '샌들', 'footwear', 3),
('loafers', 'Loafers/Flats', '로퍼/플랫', 'footwear', 4);
```

---

## products

핵심 상품 테이블. 크롤링 또는 수동 입력으로 적재.

```sql
CREATE TABLE products (
    id              TEXT PRIMARY KEY,   -- '{brand_id}_{product_code}' 형식
    brand_id        TEXT NOT NULL REFERENCES brands(id),
    season_id       TEXT REFERENCES seasons(id),
    category_id     TEXT REFERENCES categories(id),
    product_name    TEXT NOT NULL,
    product_name_kr TEXT,
    price           INTEGER,
    sale_price      INTEGER,
    currency        TEXT DEFAULT 'KRW',
    colors          TEXT,               -- JSON: ["Black", "Navy"]
    materials       TEXT,               -- JSON: ["Cotton 80%", "Polyester 20%"]
    image_urls      TEXT,               -- JSON: ["url1", "url2"]
    thumbnail_url   TEXT,
    product_url     TEXT,
    style_tags      TEXT,               -- JSON: ["minimal", "oversized"]
    description     TEXT,
    is_active       INTEGER DEFAULT 1,
    crawled_at      DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**product.id 생성 규칙:**
- 크롤링: `{brand_id}_{사이트상_상품코드}` (예: `mlb_3AWSB0143`)
- 수동입력: `{brand_id}_manual_{timestamp}` (예: `nike_manual_20250301`)

**colors 컬러 코드 정규화:**
F&F 내부 컬러 코드 체계와 매핑 가능하도록 영문 표준명 사용.
```json
["Black", "Navy", "Cream", "White", "Grey", "Beige", "Brown",
 "Red", "Blue", "Green", "Pink", "Orange", "Yellow", "Purple",
 "Khaki", "Charcoal", "Burgundy", "Camel", "Olive", "Ivory"]
```

---

## signals

시그널 시계열. target_type + target_id로 다형성 참조.

```sql
CREATE TABLE signals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type     TEXT NOT NULL CHECK(target_type IN (
        'product', 'brand', 'category', 'style_tag', 'color'
    )),
    target_id       TEXT NOT NULL,
    signal_type     TEXT NOT NULL CHECK(signal_type IN (
        'naver_search', 'musinsa_rank', 'musinsa_review',
        'sns_mention', 'celeb_wear', 'runway', 'manual'
    )),
    signal_value    REAL NOT NULL,
    signal_date     DATE NOT NULL,
    metadata        TEXT,            -- JSON: {"keyword": "배럴진", "age_group": "20-29"}
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signals_target ON signals(target_type, target_id, signal_date);
CREATE INDEX idx_signals_date ON signals(signal_date);
```

**signal_type별 signal_value 해석:**
| signal_type | value 의미 | 범위 |
|-------------|-----------|------|
| naver_search | 검색량 지수 (DataLab 기준) | 0-100 |
| musinsa_rank | 카테고리 내 랭킹 | 1-N (낮을수록 좋음) |
| musinsa_review | 리뷰 수 | 0-N |
| sns_mention | 언급 횟수 | 0-N |
| celeb_wear | 착용 셀럽 수 | 0-N |
| runway | 런웨이 등장 브랜드 수 | 0-N |
| manual | 직접 평가 점수 | 0-100 |

---

## scores

산출된 종합 스코어. 주간 단위로 스냅샷.

```sql
CREATE TABLE scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type     TEXT NOT NULL,
    target_id       TEXT NOT NULL,
    score_type      TEXT NOT NULL CHECK(score_type IN (
        'search_buzz', 'market_presence', 'manual_signal',
        'total', 'gap'
    )),
    score_value     REAL NOT NULL,
    score_date      DATE NOT NULL,
    season_id       TEXT REFERENCES seasons(id),
    components      TEXT,            -- JSON: 점수 구성 요소 분해
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scores_target ON scores(target_type, target_id, score_date);
CREATE INDEX idx_scores_season ON scores(season_id, score_type);
```

---

## predictions

예측 → 검증 루프. 시즌별 기록.

```sql
CREATE TABLE predictions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type     TEXT NOT NULL,
    target_id       TEXT NOT NULL,
    season_id       TEXT NOT NULL REFERENCES seasons(id),
    prediction_text TEXT NOT NULL,
    predicted_score REAL,
    actual_score    REAL,
    accuracy_note   TEXT,
    confidence      TEXT CHECK(confidence IN ('high', 'medium', 'low')),
    predicted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_at     DATETIME
);

CREATE INDEX idx_predictions_season ON predictions(season_id);
```

---

## 인덱스

```sql
-- products 주요 조회 패턴
CREATE INDEX idx_products_brand ON products(brand_id);
CREATE INDEX idx_products_season ON products(season_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_brand_season ON products(brand_id, season_id);
CREATE INDEX idx_products_brand_category ON products(brand_id, category_id);
```

---

## 마이그레이션

### SQLite → Snowflake 이전 시 고려사항
- `TEXT` → `VARCHAR`
- `INTEGER PRIMARY KEY AUTOINCREMENT` → `NUMBER AUTOINCREMENT`
- JSON 컬럼 → `VARIANT` 타입
- `DATETIME DEFAULT CURRENT_TIMESTAMP` → Snowflake 문법으로 변환
- 인덱스 → Snowflake는 자동 마이크로 파티셔닝 (명시적 인덱스 불필요)
- F&F 기존 Snowflake 인프라의 스키마 네이밍 컨벤션 따를 것
