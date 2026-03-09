# FTIB 스코어링 모델 상세

## 스코어링 철학

이 시스템의 스코어링은 **정확한 판매 예측이 아니다**. 목적은:
- 파이프라인의 어느 단계에 있는가를 수치로 표현
- 예측과 실제를 비교하며 유효한 시그널을 발견
- "도트가 찍히는" 위치를 시각적으로 파악

따라서 절대값보다 **상대적 순위와 변화율**이 더 중요하다.

---

## MVP 스코어링 (3요소)

### 1. Search Buzz Score (검색량, Weight: 40%)

**데이터 소스**: 네이버 DataLab API

**계산 로직:**
```
raw_ratio = 현재주 검색량 / 최근 4주 평균 검색량
score = clamp(raw_ratio × 50, 0, 100)
```

| raw_ratio | score | 해석 |
|-----------|-------|------|
| 0.0 | 0 | 검색량 없음 |
| 0.5 | 25 | 평균 대비 절반 |
| 1.0 | 50 | 평균 수준 |
| 1.5 | 75 | 50% 증가 |
| 2.0+ | 100 | 2배 이상 급등 |

**키워드 매핑 규칙:**
- 상품 단위: 상품명 + 브랜드명 조합 (예: "MLB 볼캡", "디스커버리 패딩")
- 카테고리 단위: 스타일 키워드 (예: "배럴진", "크롭 자켓")
- 브랜드 단위: 브랜드명 단독 (예: "MLB", "디스커버리")

**주의사항:**
- 네이버 DataLab은 상대적 지수(0-100)를 반환, 절대량이 아님
- 비교 기간 내 최대치가 100으로 자동 정규화됨
- 따라서 동일 키워드의 시계열 비교는 유효하나, 다른 키워드 간 직접 비교는 주의

### 2. Market Presence Score (시장 존재감, Weight: 30%)

**데이터 소스**: 크롤링된 상품 데이터 (자체 DB)

**계산 로직:**
```
category_share = 해당 스타일 상품 수 / 카테고리 전체 상품 수
price_diversity = (가격대 구간 수 - 1) / (최대 구간 수 - 1)
    가격대 구간: ~5만 / 5-10만 / 10-20만 / 20-30만 / 30만+

score = clamp(category_share × 100 × (1 + price_diversity × 0.5), 0, 100)
```

**해석:**
- 높은 점수 = 많은 브랜드가 다양한 가격대로 해당 스타일을 밀고 있음
- 낮은 점수 = 시장에 아직 해당 스타일 공급이 적음

### 3. Manual Signal Score (수동 시그널, Weight: 30%)

**데이터 소스**: 사용자 직접 입력

**입력 항목:**
- 런웨이 등장 여부 (0/20/40: 없음/일부/다수)
- 셀럽/인플루언서 착용 (0/15/30: 없음/일부/다수)
- 시장조사 인사이트 (0-30: 자유 평가)

**합산:**
```
manual_score = runway_score + celeb_score + insight_score
    (최대 100)
```

---

## 종합 스코어 & 가중치

```
Total = Search_Buzz × 0.4 + Market_Presence × 0.3 + Manual_Signal × 0.3
```

### 가중치 보정 가이드
시즌이 끝난 후 예측-실적 비교를 통해 가중치를 조정한다:

1. 예측 정확도가 높았던 시그널의 가중치를 올린다
2. 노이즈가 많았던 시그널의 가중치를 낮춘다
3. 분기별 1회 가중치 리뷰 권장

---

## Gap Score (시장 기회 지표)

**목적**: 수요는 있는데 공급이 부족한 영역 = 기회

```
Gap Score = (Search_Buzz + SNS_Signal) / max(1, Supply_Count × Competitor_Count) × 100
```

| Gap Score | 해석 |
|-----------|------|
| 80+ | 강한 기회: 수요 매우 높고 공급 극히 부족 |
| 60-79 | 보통 기회: 진입 검토 가치 있음 |
| 40-59 | 균형: 수요와 공급이 대체로 매칭 |
| 0-39 | 과잉 공급 또는 수요 부족 |

---

## Phase 2+ 확장 스코어링 (5요소)

MVP 이후 데이터가 충분히 쌓이면:

| 요소 | Weight | 소스 |
|------|--------|------|
| Runway Signal | 15% | 런웨이 등장 브랜드 수, 키 룩 포함 여부 |
| Media Buzz | 25% | 네이버 검색량 + SNS 언급량 |
| Celeb Adoption | 20% | 셀럽/인플루언서 착용 횟수 |
| Market Availability | 15% | 출시 브랜드 수, 가격대 분포, 채널 다양성 |
| Consumer Response | 25% | 무신사 랭킹, 리뷰 수 증가율, 찜 수 |

---

## 시그널 파이프라인 단계 매핑

스코어뿐 아니라 "지금 어느 단계에 있는가"를 판단하는 로직:

```python
def determine_pipeline_stage(signals: dict) -> str:
    """시그널 조합으로 현재 파이프라인 단계 판단"""
    if signals.get("runway", 0) > 0 and signals.get("market", 0) == 0:
        return "RUNWAY"      # 런웨이에만 등장
    elif signals.get("market", 0) > 0 and signals.get("buzz", 0) < 30:
        return "RELEASE"     # 출시됐지만 아직 버즈 없음
    elif signals.get("buzz", 0) >= 30 and signals.get("consumer", 0) < 50:
        return "VIRAL"       # 바이럴 시작
    elif signals.get("consumer", 0) >= 50:
        if signals.get("buzz_trend") == "rising":
            return "PEAK"    # 수요 피크
        else:
            return "SETTLE"  # 안정/하락
    return "UNKNOWN"
```
