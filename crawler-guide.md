# FTIB 크롤러 작성 가이드

## 크롤러 타입

| 타입 | 대상 | 특징 |
|------|------|------|
| `official_mall` | 브랜드 공식몰 | 사이트별 selector 커스텀 필요 |
| `musinsa` | 무신사 | 표준화된 구조, 랭킹/리뷰 데이터 풍부 |
| `wconcept` | W컨셉 | 컨템포러리 브랜드 중심 |
| `platform_generic` | 29CM, SSF샵 등 | 플랫폼별 어댑터 |

---

## 크롤러 아키텍처

```
base_crawler.py (ABC)
├── official_mall.py      # 셀렉터 기반 범용 크롤러
├── musinsa.py            # 무신사 전용
├── wconcept.py           # W컨셉 전용
└── csv_crawler.py        # CSV/엑셀 파싱 (오프라인 데이터)
```

### BaseCrawler 인터페이스

```python
class BaseCrawler(ABC):
    """모든 크롤러의 베이스 클래스"""

    brand_id: str           # 브랜드 식별자
    config: dict            # crawler_config.yaml에서 로드
    logger: Logger
    rate_limit: float       # 요청 간 딜레이 (초)

    @abstractmethod
    async def get_product_list_urls(self, season: str) -> list[str]:
        """크롤링할 상품 목록 페이지 URL 리스트 반환"""

    @abstractmethod
    async def parse_product_card(self, element) -> dict | None:
        """목록 페이지에서 상품 카드 하나 파싱. 실패 시 None."""

    @abstractmethod
    async def parse_product_detail(self, url: str, page) -> dict:
        """상세 페이지에서 추가 정보 파싱"""

    async def crawl(self, season: str = None) -> list[dict]:
        """메인 크롤링 루프 (구현됨)"""

    async def save_products(self, products: list[dict]) -> int:
        """DB 저장 (구현됨, upsert)"""

    def normalize_product(self, raw: dict) -> dict:
        """데이터 정규화 (구현됨)"""
```

---

## 새 브랜드 크롤러 추가 절차

### Step 1: 사이트 분석
1. 브라우저 DevTools로 상품 목록 페이지 구조 파악
2. 상품 카드의 CSS selector 확인
3. 페이지네이션 방식 확인 (URL 파라미터 / 무한스크롤 / 버튼)
4. 상품 상세 페이지 데이터 포인트 확인

### Step 2: config 추가
```yaml
# crawler_config.yaml에 추가
brands:
  new_brand:
    crawler_type: official_mall  # 또는 새 타입
    base_url: "https://newbrand.com/products"
    selectors:
      product_list: ".product-grid"
      product_card: ".product-item"
      product_name: ".product-item .name"
      price: ".product-item .price"
      sale_price: ".product-item .sale-price"
      image: ".product-item img[src]"
      product_link: ".product-item a[href]"
      color_chips: ".product-item .color-chip"
    pagination:
      type: "url_param"          # url_param | infinite_scroll | button
      param: "page"
      start: 1
    category_urls:
      outer: "/category/outer"
      top: "/category/top"
    schedule: weekly
    max_pages: 10
    rate_limit: 3.0              # 초
```

### Step 3: 크롤러 클래스 작성 (필요 시)
기존 `official_mall.py`의 셀렉터 기반 크롤러로 대부분 커버 가능.
특수한 사이트 구조가 있을 때만 새 클래스 작성.

### Step 4: 테스트
```bash
# 단일 브랜드 테스트 크롤링 (dry-run, DB 저장 안함)
python scripts/run_crawl.py --brand new_brand --dry-run --limit 5

# 실제 크롤링 (DB 저장)
python scripts/run_crawl.py --brand new_brand --season 2025SS
```

---

## 데이터 정규화 규칙

### 상품명 정규화
```python
def normalize_product_name(raw_name: str) -> tuple[str, str]:
    """원본 상품명 → (영문명, 한글명) 분리"""
    # 예: "[MLB] 클래식 모노그램 볼캡" → ("Classic Monogram Ball Cap", "클래식 모노그램 볼캡")
    # 브랜드 프리픽스 제거: [MLB], [Discovery] 등
    # 한영 분리
```

### 가격 정규화
```python
def normalize_price(raw_price: str) -> int:
    """'89,000원', '₩89,000', '89000' → 89000"""
    return int(re.sub(r'[^\d]', '', raw_price))
```

### 컬러 정규화
```python
COLOR_MAP = {
    # 한글 → 영문 표준
    "블랙": "Black", "검정": "Black", "BK": "Black",
    "네이비": "Navy", "NV": "Navy",
    "화이트": "White", "흰색": "White", "WH": "White",
    "크림": "Cream", "아이보리": "Ivory",
    "베이지": "Beige", "BG": "Beige",
    "그레이": "Grey", "회색": "Grey", "GR": "Grey",
    # ... 확장
}
```

### 카테고리 매핑
```python
CATEGORY_MAP = {
    # 사이트별 카테고리명 → DB categories.id
    "자켓": "outer", "점퍼": "outer", "코트": "outer", "패딩": "outer",
    "티셔츠": "top", "셔츠": "top", "니트": "top", "맨투맨": "top",
    "팬츠": "bottom", "진": "bottom", "스커트": "bottom",
    "원피스": "dress",
    "백": "bag", "가방": "bag",
    "캡": "hat", "모자": "hat",
    # ... 확장
}
```

---

## 에러 핸들링

```python
async def safe_parse(self, element, selector: str, default="") -> str:
    """안전한 셀렉터 파싱 — 실패 시 기본값 반환"""
    try:
        el = await element.query_selector(selector)
        if el:
            return (await el.inner_text()).strip()
        return default
    except Exception:
        return default
```

### 로깅 규칙
```python
# 레벨별 사용 기준
self.logger.info(f"Crawling {brand_id}: page {page_num}")      # 진행 상황
self.logger.warning(f"Missing price for {product_url}")          # 데이터 누락 (계속 진행)
self.logger.error(f"Page load failed: {url} - {e}")             # 페이지 실패 (skip)
self.logger.critical(f"Browser crashed: {e}")                    # 전체 중단
```

---

## 무신사 크롤러 특이사항

무신사는 구조가 비교적 표준화되어 있어 추가 데이터 수집 가능:
- **랭킹**: 카테고리별 베스트 순위
- **리뷰 수**: 상품별 리뷰 카운트
- **좋아요(찜) 수**: 상품 인기 지표
- **최근 구매 수**: 일부 노출되는 경우

이 데이터는 `signals` 테이블에 별도 저장:
```python
# 무신사 랭킹 시그널
signal = {
    "target_type": "product",
    "target_id": product_id,
    "signal_type": "musinsa_rank",
    "signal_value": rank_position,
    "signal_date": today,
    "metadata": json.dumps({"category": "outer", "subcategory": "jacket"})
}
```
