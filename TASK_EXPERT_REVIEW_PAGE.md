# TASK: Expert Report Review 페이지 신규 개발

> Claude Code 작업 지시서
> 관련 문서: CLAUDE.md, WGSN_26SS_KEYWORD_MASTER.md

---

## 목표

WGSN 등 전문가 리포트 분석 결과를 팀원들과 함께 리뷰·보정할 수 있는 페이지를 새로 만든다.
현재는 WGSN 77건 기반 초안이며, 향후 Tagwalk/Vogue/BoF 등 소스를 추가하거나
키워드를 엄선/보정하는 작업을 이 페이지에서 반복적으로 수행한다.

---

## 신규 페이지 스펙

### 페이지 정보

| 항목 | 값 |
|------|-----|
| 페이지명 | Expert Report Review |
| 경로 | `/expert` |
| 사이드바 위치 | Trend Flow와 Runway 사이 |
| 데이터 소스 | 시드 데이터 (JSON) → 향후 expert_reports/expert_keywords 테이블 연동 |

### 전체 구조 (3단계 drill-down)

```
Level 1: 필터 바
  ├── 시즌 선택 (pill 토글): 24SS ~ 26FW (기본값: 26SS)
  ├── 카테고리 탭: 전체 | 컬러 | 소재 | 실루엣 | 아이템 | 스타일
  └── 소스 필터 (향후): WGSN | Tagwalk | Vogue | BoF | Pantone | 전체

Level 2: 키워드 카드 그리드
  ├── Tier별 섹션 구분 (Tier 1 핵심 합의 / Tier 2 주요 / Tier 3 서브)
  ├── 각 카드: 키워드명, 소스 수, 카테고리 태그, 풀 A/B 태그
  └── 정렬: 소스 수 내림차순 (기본)

Level 3: 키워드 상세 패널 (카드 클릭 시)
  ├── 키워드 기본 정보 (카테고리, 소스 수, Tier, 풀 A/B)
  ├── WGSN 테마 매핑 (어떤 매크로 테마에 속하는지)
  ├── 설명 텍스트 (WGSN 리포트 요약)
  ├── 런웨이 연관도 (향후: VLM 데이터 매칭 수)
  ├── 마켓 연관도 (향후: 마켓 상품 매칭 수)
  └── 팀 리뷰 액션
      ├── 평가: 핵심 | 참고 | 제외 (3단계)
      ├── 코멘트 입력
      └── 평가자 이름
```

### Level 2: 키워드 카드 상세

```jsx
<ExpertKeywordCard>
  <Top>
    <KeywordName>Sheer</KeywordName>
    <SourceCount>11개 소스</SourceCount>
  </Top>
  
  <Tags>
    <CategoryTag>material</CategoryTag>
    <TierTag>Tier 1</TierTag>
    <PoolTag>풀 A</PoolTag>  // 또는 풀 B, 미분류
  </Tags>
  
  <Description>
    시폰, 오간자 — 레이어링, Day-to-Night 핵심 소재
  </Description>
  
  <ReviewStatus>  // 팀 리뷰 후 표시
    <Badge>핵심</Badge>  // 또는 참고, 제외, 미평가
  </ReviewStatus>
</ExpertKeywordCard>
```

그리드: `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`

### Level 3: 상세 패널

카드 클릭 시 그리드 아래에 패널이 열림 (TrendFlowCheck의 KeywordDetailPanel과 동일 패턴).

```jsx
<ExpertKeywordDetail keyword="sheer">
  <Header>
    <Title>Sheer (시어/투명 소재)</Title>
    <Subtitle>material · Tier 1 · 풀 A · 11개 소스</Subtitle>
  </Header>
  
  <Section title="WGSN 분석 요약">
    <p>초경량 시폰, 오간자 등을 활용해 섬세한 레이어링과 입체적인 
    볼륨감을 연출하며 이번 시즌 가장 지배적인 패브릭으로 꼽힘.
    Day-to-Night 룩을 위한 핵심 소재.</p>
  </Section>
  
  <Section title="매크로 테마 연결">
    <ThemeTag>Pretty Feminine</ThemeTag>
    <ThemeTag>City To Beach</ThemeTag>
  </Section>
  
  <Section title="관련 데이터 (향후 연동)">
    <DataRow label="런웨이 VLM 매칭" value="— (연동 예정)" />
    <DataRow label="마켓 상품 매칭" value="— (연동 예정)" />
  </Section>
  
  <Section title="팀 리뷰">
    <RadioGroup name="evaluation">
      <Radio value="essential">핵심 — F&F 브랜드에 직접 해당</Radio>
      <Radio value="reference">참고 — 알아두면 좋음</Radio>
      <Radio value="exclude">제외 — 우리와 무관</Radio>
    </RadioGroup>
    <TextInput placeholder="코멘트 (선택)" />
    <TextInput placeholder="평가자 이름" />
    <Button>평가 저장</Button>
  </Section>
  
  <Actions>
    <Button onClick={navigateToRunway}>런웨이에서 확인</Button>
    <Button onClick={navigateToBrandBoard}>마켓에서 확인</Button>
  </Actions>
</ExpertKeywordDetail>
```

---

## 데이터 구조

### 시드 데이터 형식

초기에는 JSON 시드 데이터로 시작. 아래 형식으로 `expertKeywordsData.js` 파일 생성.

```js
export const EXPERT_KEYWORDS_26SS = [
  {
    keyword: "sheer",
    keyword_kr: "시어/투명 소재",
    category: "material",    // color | material | silhouette | item | style
    season: "26SS",
    source_count: 11,
    tier: 1,                 // 1, 2, 3
    pool: "A",               // "A", "B", null
    source: "wgsn",
    themes: ["Pretty Feminine", "City To Beach"],
    description: "초경량 시폰, 오간자 등을 활용해 섬세한 레이어링과 입체적인 볼륨감을 연출하며 이번 시즌 가장 지배적인 패브릭",
    runway_keyword: "sheer", // FTIB synonym map 매칭용 키워드
    f_and_f_relevance: null, // "high", "medium", "low", null
    review_status: null,     // "essential", "reference", "exclude", null
    review_comment: null,
    reviewer: null,
  },
  // ... 전체 키워드
];
```

### WGSN_26SS_KEYWORD_MASTER.md 참조

위 마크다운 문서의 전체 키워드를 JSON으로 변환하여 시드 데이터 생성.
카테고리별 키워드 수 (예상):
- 컬러: ~35개
- 소재: ~25개
- 실루엣: ~20개
- 아이템: ~25개
- 스타일(매크로 테마): ~15개
- **합계: ~120개 키워드**

---

## 백엔드 API

### 신규 라우터: `backend/api/routes/expert.py`

```
GET /api/expert/keywords
  ?season=26SS
  ?category=material
  ?tier=1
  ?pool=A
  → 키워드 목록 반환

GET /api/expert/keyword/{keyword}/detail
  → 키워드 상세 정보 반환

POST /api/expert/keyword/{keyword}/review
  body: { evaluation, comment, reviewer, season }
  → 팀 리뷰 저장
```

초기에는 시드 데이터에서 직접 반환.
향후 expert_keywords 테이블로 마이그레이션.

---

## 프론트엔드 파일 구조

```
frontend/src/
├── pages/
│   └── ExpertReview.jsx          ← 신규 페이지
├── components/expert/
│   ├── ExpertFilterBar.jsx       ← 시즌 + 카테고리 + 소스 필터
│   ├── ExpertKeywordCard.jsx     ← 키워드 카드
│   ├── ExpertKeywordGrid.jsx     ← Tier별 섹션 + 그리드
│   ├── ExpertKeywordDetail.jsx   ← 상세 패널
│   └── expertKeywordsData.js     ← 시드 데이터 (JSON)
└── hooks/
    └── useExpertKeywords.js      ← 데이터 fetch + 필터 로직
```

---

## 라우터 등록

```jsx
// App.jsx 또는 router 설정에 추가
{ path: "/expert", element: <ExpertReview /> }

// Sidebar.jsx에 추가
// Trend Flow와 Runway 사이 위치
{ name: "Expert Review", path: "/expert", icon: "📊" }
```

---

## 크로스 페이지 연결

```
Expert Review → Runway: /runway?tag={keyword}&season=26SS
Expert Review → Brand Board: /?keyword={keyword}
Expert Review → Trend Flow check: /flow-check (키워드 비교)
```

---

## 구현 우선순위

### Phase 1 (이번 작업)
1. 시드 데이터 JSON 생성 (WGSN_26SS_KEYWORD_MASTER.md 기반)
2. ExpertReview 페이지 + 컴포넌트 생성
3. 필터바 + 카드 그리드 + 상세 패널
4. 팀 리뷰 기능 (로컬 상태 — 새로고침 시 초기화 OK)
5. 라우터 + 사이드바 등록

### Phase 2 (향후)
- 백엔드 API 연동 (expert_keywords 테이블)
- 리뷰 결과 DB 저장
- 런웨이 VLM 매칭 수 연동
- 마켓 상품 매칭 수 연동
- 추가 소스(Tagwalk, Vogue 등) 데이터 적재

---

## 참고 사항

- TrendFlowCheck.jsx의 4단계 drill-down 패턴을 참고하여 일관된 UX 유지
- 기존 KeywordCard, KeywordDetailPanel 컴포넌트 스타일 참고
- Tailwind CSS v4 사용
- 모바일 반응형은 Phase 2에서
