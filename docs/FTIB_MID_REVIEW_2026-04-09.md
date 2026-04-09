# Deep Interview Spec: FTIB 프로젝트 중간 점검

## Metadata
- Interview ID: di-midreview-2026-04-09
- Rounds: 9
- Final Ambiguity Score: 18%
- Type: brownfield
- Generated: 2026-04-09
- Threshold: 20%
- Status: PASSED

## Clarity Breakdown
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.90 | 0.35 | 0.315 |
| Constraint Clarity | 0.75 | 0.25 | 0.188 |
| Success Criteria | 0.80 | 0.25 | 0.200 |
| Context Clarity | 0.80 | 0.15 | 0.120 |
| **Total Clarity** | | | **0.823** |
| **Ambiguity** | | | **17.7%** |

---

## 점검 결론: 방향 전환 권고

### 현재 상태 진단

**데이터 수집 인프라**: 탁월 (90% 완성)
- 마켓 35 브랜드, 11,565 상품
- 런웨이 TagWalk 13,882 + Vogue 47,519 = 61,401 이미지
- VLM 라벨 10,094개, 전문가 키워드 101개

**트렌드 전파 분석**: 미흡 (10% 수준)
- Confidence 점수: mock 데이터
- Origin 분류: 로직만 존재, 실행 안 됨
- 시간축 전파 추적: 미구현

**핵심 문제**: 데이터 수집에 80% 이상의 시간을 투자했지만, 프로젝트의 원래 목적인 "트렌드 전파 정량적 추적"은 아직 증명되지 않았음.

### 방향 전환: 수집 → 분석/증명

| 기존 방향 | 새 방향 |
|-----------|---------|
| 더 많은 브랜드 크롤링 (Hyperbrowser 도입 등) | 현재 데이터로 "전파 증명" 먼저 |
| VLM 범용 키워드 (leather, oversized) | 세분화된 트렌드 키워드 (오픈백 가방, 뾰족한 토 구두) |
| Confidence 5-signal 가중치 공식 | 구체적 사례 기반 시간축 타임라인 |
| 종합 대시보드 완성 | 5~10개 핵심 트렌드 스토리로 검증 |

---

## 3가지 산출물

### 1. 결정 리스트

| 영역 | 결정 | 근거 |
|------|------|------|
| **데이터 수집** | 일시 중단 (Hyperbrowser 도입 보류) | 현재 데이터로 분석 증명이 우선 |
| **VLM 키워드** | 세분화 필요 — 범용 키워드 → 구체적 트렌드 아이템 | 팀 동료 정성 분석에서 세부 키워드가 실제 트렌드와 일치 확인 |
| **Confidence 점수** | 시기상조 → 보류 | 5개 시그널 가중치보다 시간축 전파 사례가 더 설득력 |
| **Trend Flow 페이지** | 재설계: mock → 실데이터 타임라인 | 프로젝트 핵심 가치를 보여주는 페이지 |
| **Expert Review** | 팀 동료 정성 분석 결과를 데이터화 | 현재 가장 가치 있는 검증 작업 |
| **마켓 크롤링 확대** | 분석 결과에 따라 필요한 조닝만 선택적 확대 | "일단 전부 수집"에서 "증명에 필요한 것만" |
| **셀럽/인플루언서** | 구체적 트렌드 5~10개에 대해서만 수동+AI 수집 | 전체 수집보다 사례 중심 접근 |

### 2. 향후 로드맵

**Phase A: 증명 (4~6주)**

핵심: "런웨이 키워드가 마켓에 전파된다"를 5~10개 구체적 사례로 증명

| Week | 작업 | 담당 | 산출물 |
|------|------|------|--------|
| 1-2 | 팀 동료 정성 분석 → 구조화 | 동료+본인 | 검증된 트렌드 사례 10개 리스트 (키워드, 런웨이 출처, 마켓 증거) |
| 2-3 | VLM 키워드 세분화 개선 | 본인 | 프롬프트 개선 → 구체적 아이템/디테일 추출 |
| 3-4 | 시즌별 전파 타임라인 구축 | 본인 | 키워드별 런웨이(24SS)→마켓(25SS) 빈도 변화 시각화 |
| 4-6 | Trend Flow 페이지 재설계 | 본인 | 실데이터 기반 타임라인 대시보드 |

**Phase B: 확장 (Phase A 성공 후)**

| 작업 | 조건 | 내용 |
|------|------|------|
| 셀럽/인플루언서 데이터 | Phase A에서 전파 패턴 확인 시 | 검증된 트렌드에 대해 셀럽 착용 데이터 수집 |
| 마켓 브랜드 확대 | 특정 조닝에서 데이터 부족 확인 시 | Hyperbrowser로 해당 조닝만 선택적 확대 |
| Confidence 점수 실데이터화 | 타임라인 패턴이 안정화된 후 | 빈도 기반 단순 점수부터 시작 |
| Origin 자동 분류 | 충분한 사례 축적 후 | 수동 분류 → 패턴 학습 → 자동화 |

**Phase C: 고도화 (6개월+)**
- 검색량 데이터 연동 (Naver DataLab)
- 실시간 모니터링 대시보드
- 예측 모델 (다음 시즌 트렌드 예측)

### 3. 스토리텔링

**팀/상사에게 설명하는 논리:**

> "패션 트렌드가 런웨이에서 시작해서 마켓으로 퍼지는 건 업계의 상식이지만, 이걸 정량적으로 추적한 사례는 없습니다.
>
> 우리는 54개 디자이너의 6시즌 런웨이 데이터(6만+ 이미지)와 35개 마켓 브랜드의 상품 데이터(11,000+)를 AI로 분석해서, 실제로 런웨이 키워드가 마켓으로 전파되는 패턴을 확인했습니다.
>
> 예를 들어, 26SS 런웨이에서 두드러진 '오픈백 가방', '뾰족한 토 구두' 같은 구체적 트렌드가 현재 마켓에서 실제로 증가하고 있음을 확인했습니다.
>
> 다음 단계는 이런 전파 패턴을 시간축으로 시각화해서, 패션 기업이 '어떤 트렌드가 지금 마켓에 도달하고 있는지'를 실시간으로 파악할 수 있는 대시보드를 만드는 것입니다."

---

## Assumptions Exposed & Resolved

| Assumption | Challenge | Resolution |
|------------|-----------|------------|
| 더 많은 데이터 수집이 우선 | Contrarian: 수집보다 증명이 먼저 아닌가? | 분석/증명 우선으로 전환. 수집은 필요시 선택적 확대 |
| VLM 범용 키워드로 매칭 가능 | 팀 동료 검증: "너무 뻔한 결과" | 세분화 필요 — 구체적 아이템/디테일 수준으로 |
| Confidence 5-signal 공식이 핵심 | 사용자 판단: "현재 수준에서 너무 막연" | 시기상조 → 사례 기반 타임라인이 먼저 |
| 전체 시그널(5개) 모두 필요 | Simplifier: 최소한으로 증명 가능한 것은? | 런웨이→마켓 2개 시그널만으로 먼저 증명 |
| 개인 프로젝트 | 실제: 2~3명 팀, 동료가 도메인 분석 담당 | 역할 분담: 본인=기술/데이터, 동료=도메인/정성분석 |

## Technical Context

### 현재 활용 가능한 데이터
- `runway_looks`: 13,882개 (TagWalk, 40 designers × 6 seasons)
- `vogue_runway_images`: 47,519개 (317 shows, collection+detail+beauty)
- `vlm_labels`: 10,094개 (item/shape/size/color/texture)
- `products`: 11,565개 (35 brands, name/color/material/category)
- `expert_keywords`: 101개 WGSN 키워드 (Pool A 49, Pool B 12)

### 현재 부족한 데이터
- `celeb_sightings`: 비어있음 (스키마만 존재)
- `celeb_search_volume`: 비어있음
- `keyword_signals`: 비어있음 (시간축 데이터)
- 마켓 상품의 시즌별 변화 데이터 (현재 스냅샷만)

### VLM 개선 필요 사항
- 현재: "bag", "leather", "black" 수준의 범용 키워드
- 필요: "open-back structured bag", "pointed-toe kitten heel", "dewy no-makeup" 수준의 세분화
- 방법: VLM 프롬프트 개선 + Vogue 디테일 샷 활용 (해상도 높은 클로즈업)

## Ontology (Key Entities)

| Entity | Type | Fields | Relationships |
|--------|------|--------|---------------|
| Trend Keyword | core | name, category, granularity, source | appears in Runway, tracked in Market |
| Runway Collection | data source | designer, season, looks, VLM labels | produces Trend Keywords |
| Market Product | data source | brand, name, color, material, season | validates Trend Keywords |
| Propagation Timeline | analysis | keyword, season_start, signal_sequence, velocity | connects Runway→Market |
| VLM Label | processing | item, shape, color, texture, granularity | extracts Trend Keywords from images |
| Expert Keyword | validation | keyword, pool (A/B), tier, confidence | validates/predicts Trend Keywords |
| Team Member | actor | role (domain/tech), current_task | performs Analysis |
| Qualitative Validation | process | keyword, runway_evidence, market_evidence, verdict | bridges qualitative→quantitative |
| Quantification Framework | deliverable | timeline_view, zoning_breakdown, case_studies | presents Propagation Timeline |
| Zoning | taxonomy | name, brands[], coverage | segments Market analysis |
| Celebrity/Influencer | data source (future) | name, tier, keyword, sighting_date | fills Propagation Timeline gap |
| Dashboard | deliverable | pages, filters, visualizations | presents everything to team |

## Interview Transcript
<details>
<summary>Full Q&A (9 rounds)</summary>

### Round 1
**Q:** 이번 중간 점검의 결과물로 기대하는 것이 뭐예요?
**A:** 방향 전환 검토
**Ambiguity:** 79% (Goal: 0.35, Constraints: 0.05, Criteria: 0.10, Context: 0.30)

### Round 2
**Q:** 현재 방향에 의문을 갖게 된 구체적인 계기가 있나요?
**A:** 종합적 재평가
**Ambiguity:** 73% (Goal: 0.40, Constraints: 0.20, Criteria: 0.10, Context: 0.35)

### Round 3
**Q:** 이 중간 점검이 끝났을 때, 어떤 형태의 결론이 나오면 성공인가요?
**A:** 복합 (결정 + 로드맵 + 스토리)
**Ambiguity:** 57% (Goal: 0.55, Constraints: 0.20, Criteria: 0.50, Context: 0.40)

### Round 4
**Q:** 이 프로젝트를 진행하는 팀 구성과 상황이 궁금합니다.
**A:** 소규모 팀 (2~3명)
**Ambiguity:** 50% (Goal: 0.55, Constraints: 0.45, Criteria: 0.50, Context: 0.45)

### Round 5 [CONTRARIAN MODE]
**Q:** 데이터 수집을 멈추고 지금 있는 데이터로 "전파 정량화"를 먼저 증명하는 게 더 중요하지 않나요?
**A:** 분석/증명 우선
**Ambiguity:** 42% (Goal: 0.70, Constraints: 0.50, Criteria: 0.55, Context: 0.50)

### Round 6
**Q:** FTIB가 "트렌드 전파를 정량적으로 추적한다"를 증명하려면 가장 먼저 보여줘야 할 것은?
**A:** 런웨이→마켓 사례 증명
**Ambiguity:** 35% (Goal: 0.80, Constraints: 0.50, Criteria: 0.65, Context: 0.55)

### Round 7 [SIMPLIFIER MODE]
**Q:** "전파 증명"의 가장 단순한 버전은 VLM 키워드 × 마켓 교차 확인. 이 수준이면 충분한가요?
**A:** 교차확인만으로는 부족. 시간축 + 정량 + 참고 이미지/링크까지 필요. 팀 동료가 정성 검증 진행 중.
**Ambiguity:** 28% (Goal: 0.85, Constraints: 0.55, Criteria: 0.75, Context: 0.65)

### Round 8
**Q:** 셀럽/인플루언서 데이터는 어떻게 확보할 계획인가요?
**A:** 팀 동료가 런웨이 키워드를 AI분석+디자이너 코멘트+전문가 아티클과 비교하며 정성 분석 중. 상당히 일치하지만 정량적 형태로 보여주는 방법이 고민. VLM 키워드가 너무 범용적이라 매칭 대시보드가 뻔할 것 같다는 우려.
**Ambiguity:** 22% (Goal: 0.90, Constraints: 0.65, Criteria: 0.75, Context: 0.75)

### Round 9
**Q:** 정량화 프레임워크에서 가장 먼저 만들어야 할 것은?
**A:** VLM 키워드가 범용적이어서 세분화 필요. 오픈백 가방, 뾰족한 토 구두, 노메이크업 등 구체적 키워드는 실제 트렌드와 일치. Confidence보다 시간축 타임라인이 먼저. 팀 전체가 공감할 수 있는 구성이 핵심.
**Ambiguity:** 18% (Goal: 0.90, Constraints: 0.75, Criteria: 0.80, Context: 0.80)

</details>
