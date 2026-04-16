/* ── 프로젝트 데이터 ── */
const PROJECT = {
  title: "Fashion Trend Intelligence Board",
  subtitle: "Runway-led 트렌드 전파를 데이터 기반으로 추적·검증하는 대시보드",
  version: "v2.0",
  lastUpdate: "2026-04-09",
};

const HYPOTHESIS = {
  core: "런웨이 시그널 → 셀럽 / 인플루언서 → 디자이너 브랜드 → 일반 SNS",
  description: "하이엔드 런웨이에서 시작된 트렌드 키워드가 셀럽·인플루언서 착용 → 소규모 디자이너 브랜드 상품화 → 일반인 구매·착용 SNS 확산으로 이어지는 전파 경로를 시간축으로 정량 추적합니다.",
  origins: [
    { type: "Runway-led", flow: "런웨이 → 셀럽 → 디자이너 브랜드 → 일반 SNS", delay: "3~6개월", color: "#3266ad", zoning: "핵심 검증 대상" },
  ],
  archived: [
    { type: "Capital-driven", flow: "브랜드 투자 → 캠페인 → 검색 폭발 → 마켓", note: "상품개발 시점과 비교해 의미 낮음 → 참고용", color: "#8B5CF6" },
    { type: "Viral / Meme", flow: "소셜 밈 → 틱톡 확산 → 검색 급등 → 마켓 소진", note: "예측·대응이 불가한 구조 → 참고용", color: "#D97706" },
    { type: "Market-organic", flow: "소비자 수요 → 마켓 점진 확대", note: "향후 별도 프로젝트에서 디벨롭 예정", color: "#059669" },
  ],
};

const DATA_STATS = [
  { label: "런웨이", value: "61,401", sub: "TagWalk 13,882 + Vogue 47,519" },
  { label: "마켓 상품", value: "11,565", sub: "35개 브랜드" },
  { label: "VLM 라벨", value: "10,094", sub: "AI 이미지 분석" },
  { label: "전문가 키워드", value: "101", sub: "WGSN 26SS 분석" },
];

const PAGES = [
  {
    name: "Trend Flow",
    path: "/flow",
    status: "live",
    highlight: true,
    description: "Runway-led 트렌드 전파 흐름을 모니터링합니다. 런웨이 → 셀럽 → SNS → 디자이너 브랜드.",
    features: ["Runway-led 전파 타임라인", "키워드별 전파 단계 추적", "검증 진행 상황 대시보드"],
  },
  {
    name: "Runway",
    path: "/runway",
    status: "live",
    highlight: true,
    description: "TagWalk + Vogue Runway + VLM 분석을 3개 탭으로 통합한 런웨이 데이터 허브.",
    features: ["TagWalk 13,882 룩", "Vogue 47,519 이미지 (디테일 포함)", "VLM AI 라벨 분석"],
  },
  {
    name: "Expert Review",
    path: "/expert",
    status: "live",
    description: "WGSN 26SS 리포트 기반 101개 키워드 요약. 참고용 데이터.",
    features: ["키워드 카테고리 분포 차트", "Pool A/B 분류", "Tier별 키워드 요약"],
  },
  {
    name: "Market Brand Board",
    path: "/market",
    status: "live",
    highlight: true,
    description: "35개 브랜드의 마켓 상품을 조닝별로 탐색합니다. 디자이너 브랜드 중심 검증 예정.",
    features: ["조닝별 브랜드 하이어라키", "카테고리 8 중분류", "디자이너 브랜드 검증 대상"],
  },
];

const KEYWORD_STANDARD = {
  title: "검증 방향 전환 — 왜 디자이너 브랜드인가?",
  description: "매스 브랜드(Nike, Zara 등)는 생산 리드타임 6~12개월 + 조직 의사결정 느림으로 트렌드 검증에 부적합. 소규모 디자이너 브랜드가 하이엔드 트렌드를 빠르게 재해석하는 실제 전파 경로를 추적합니다.",
  streams: [
    {
      label: "런웨이 키워드 (AI + 쇼노트)",
      source: "VLM 이미지 분석 + 디자이너 쇼 노트 교차",
      lang: "영문/한글",
      example: "오픈백 가방, 뾰족한 토 구두, 시어 드레스",
      status: "세분화 진행 중",
      color: "#3266ad",
    },
    {
      label: "셀럽/인플루언서 착용",
      source: "SNS 모니터링 + 수동 검증",
      lang: "-",
      example: "셀럽 A의 레더 재킷, 인플루언서 B의 시스루 룩",
      status: "팀 동료 분석 중",
      color: "#8B5CF6",
    },
    {
      label: "디자이너 브랜드 상품화",
      source: "국내 캐주얼/스트리트 브랜드 크롤링",
      lang: "한글",
      example: "Youth, Coor, Mardi, Blankroom 등",
      status: "기존 데이터 활용 + 검증 대상 재정의",
      color: "#059669",
    },
  ],
  goal: "런웨이 키워드가 셀럽 → SNS → 디자이너 브랜드로 전파되는 시간축 타임라인을 구축",
};

const TIMELINE = [
  { phase: "Phase 1", period: "3/11 ~ 4/8", label: "데이터 수집 인프라", status: "done",
    items: ["35개 브랜드 마켓 크롤링 (11,565 상품)", "TagWalk 13,882 + Vogue 47,519 런웨이 이미지", "VLM 라벨링 10,094개 완료", "WGSN 101 키워드 분석 완료"] },
  { phase: "Phase 2", period: "4/9 ~ 진행중", label: "Runway-led 검증 전환", status: "active",
    items: ["핵심 가설 Runway-led 전파로 집중", "팀 동료 정성 분석 (26SS 33브랜드 교차검증)", "셀럽/인플루언서 풀 설정 및 수집 방법 정의", "검증 대상: 매스 브랜드 → 디자이너 브랜드로 전환"] },
  { phase: "Phase 3", period: "4~5월", label: "전파 타임라인 증명", status: "upcoming",
    items: ["핵심 트렌드 5~10개 사례 기반 시간축 추적", "런웨이 → 셀럽 → SNS → 디자이너 브랜드 전파 정량화", "VLM 키워드 세분화 (범용 → 구체적 아이템/디테일)"] },
  { phase: "Phase 4", period: "5~6월", label: "대시보드 고도화", status: "upcoming",
    items: ["Trend Flow 실데이터 타임라인 대시보드", "셀럽/인플루언서 모니터링 통합", "디자이너 브랜드 중심 마켓 검증 뷰"] },
];

const VERIFICATION = [
  { step: "1", title: "런웨이 데이터 수집", status: "done", detail: "TagWalk 13,882 + Vogue 98,883 이미지 (131 디자이너, 디테일 샷 포함)" },
  { step: "2", title: "AI + 전문가 키워드 추출", status: "done", detail: "VLM 10,094 라벨 + WGSN 101 키워드 + 디자이너 쇼 노트" },
  { step: "3", title: "셀럽/인플루언서 전파 확인", status: "active", detail: "AI 추출 트렌드를 셀럽 착장에서 수기 검증 예정" },
  { step: "4", title: "디자이너 브랜드 마켓 검증", status: "active", detail: "무신사 240 브랜드 수집 완료, 키워드 매칭 분석 중" },
  { step: "5", title: "일반 SNS 확산 모니터링", status: "upcoming", detail: "인스타/틱톡/샤오홍수 — 타 팀 수집 데이터 연계 예정" },
];

const AI_INSIGHTS = {
  title: "AI 이미지 분석 vs 전문가 리포트 — 테스트 결과",
  sections: [
    {
      label: "1. WGSN 전문가 리포트 분석",
      status: "done",
      color: "#D97706",
      finding: "300여개 리포트 중 77개를 NotebookLM으로 분석. 컬러 28개, 소재 20개, 실루엣 18개 등 101개 키워드 도출.",
      limitation: "너무 광범위한 주제를 다루어 일반적 결론 위주로 수렴. 실무에서 바로 활용하기엔 추상적.",
    },
    {
      label: "2. AI 런웨이 이미지 직접 분석",
      status: "done",
      color: "#3266ad",
      finding: "쇼의 분위기/의도/사회적 맥락은 파악 불가. 하지만 이미지로 확인 가능한 정량적 부분(아이템, 컬러, 소재, 실루엣)은 정확하게 감지.",
      limitation: "디자이너가 '왜' 그 선택을 했는지는 이미지만으로는 알 수 없음.",
    },
    {
      label: "3. 디자이너 쇼 노트로 맥락 보완",
      status: "done",
      color: "#059669",
      finding: "디자이너가 직접 발표한 쇼의 의도/맥락 데이터 확보. 별도 AI 분석 없이 원문 그대로 사용 가능한 수준.",
      limitation: "모든 쇼에 노트가 있지는 않음. 주요 하우스 위주.",
    },
  ],
  conclusion: "추상적 전문가 리포트보다 이미지 기반 팩트 + 쇼 노트 맥락의 조합이 실무자에게 더 효율적인 인사이트를 제공.",
  nextSteps: [
    { step: "셀럽/인플루언서 착장 검증", detail: "AI가 추출한 아이템/트렌드가 실제 셀럽 착용에서 보이는지 수기 확인 예정", status: "active" },
    { step: "디자이너 브랜드 마켓 검증", detail: "무신사 240개 브랜드에서 키워드 매칭 + 신규 상품 진입 추이 분석 중", status: "active" },
    { step: "전파 타임라인 구축", detail: "런웨이 → 셀럽 → 디자이너 브랜드 시간축 정량화", status: "upcoming" },
  ],
};

/* ── 컴포넌트 ── */
const STATUS_STYLE = {
  done: { bg: "bg-emerald-100", text: "text-emerald-700", label: "완료" },
  active: { bg: "bg-blue-100", text: "text-blue-700", label: "진행 중" },
  partial: { bg: "bg-amber-100", text: "text-amber-700", label: "부분 완료" },
  upcoming: { bg: "bg-gray-100", text: "text-gray-500", label: "예정" },
  live: { bg: "bg-emerald-100", text: "text-emerald-700", label: "Live" },
  beta: { bg: "bg-amber-100", text: "text-amber-700", label: "Beta" },
  pending: { bg: "bg-gray-100", text: "text-gray-400", label: "고도화 예정" },
};

function Badge({ status }) {
  const s = STATUS_STYLE[status] || STATUS_STYLE.upcoming;
  return (
    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${s.bg} ${s.text}`}>
      {s.label}
    </span>
  );
}

export default function ProjectBriefing() {
  return (
    <main className="flex-1 overflow-y-auto bg-[var(--color-bg)]">
      <div className="max-w-[960px] mx-auto px-8 py-10">

        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center gap-3 mb-2">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2">
              <path d="M12 3l1.5 4.5H18l-3.5 2.5L16 14.5 12 12l-4 2.5 1.5-4.5L6 7.5h4.5z" />
            </svg>
            <h1 className="font-['Lora'] text-2xl font-bold tracking-wide">{PROJECT.title}</h1>
            <span className="text-[10px] px-2 py-0.5 rounded bg-[var(--color-primary)]/10 text-[var(--color-primary)] font-medium">
              {PROJECT.version}
            </span>
          </div>
          <p className="text-sm text-[var(--color-text-secondary)]">{PROJECT.subtitle}</p>
          <p className="text-[11px] text-[var(--color-text-muted)] mt-1">Last Updated: {PROJECT.lastUpdate}</p>
        </div>

        {/* Data Stats */}
        <div className="grid grid-cols-4 gap-4 mb-10">
          {DATA_STATS.map((s) => (
            <div key={s.label} className="bg-white border border-[var(--color-border)] rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-[var(--color-text)] font-['Lora']">{s.value}</div>
              <div className="text-xs font-medium text-[var(--color-text-secondary)] mt-1">{s.label}</div>
              <div className="text-[10px] text-[var(--color-text-muted)] mt-0.5">{s.sub}</div>
            </div>
          ))}
        </div>

        {/* Hypothesis */}
        <section className="mb-10">
          <h2 className="font-['Lora'] text-lg font-semibold mb-4">핵심 가설 — 트렌드 전파 파이프라인</h2>
          <div className="bg-white border border-[var(--color-border)] rounded-lg p-5 mb-4">
            <div className="flex items-center gap-2 flex-wrap text-sm font-medium">
              {HYPOTHESIS.core.split(" → ").map((step, i, arr) => (
                <span key={i} className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-md bg-[var(--color-primary)]/8 text-[var(--color-primary)] text-xs font-semibold">
                    {step}
                  </span>
                  {i < arr.length - 1 && <span className="text-[var(--color-text-muted)]">→</span>}
                </span>
              ))}
            </div>
            <p className="text-xs text-[var(--color-text-secondary)] mt-3">{HYPOTHESIS.description}</p>
          </div>
          {/* Runway-led 핵심 검증 */}
          <div className="mb-4">
            {HYPOTHESIS.origins.map((o) => (
              <div key={o.type} className="border-2 border-[#3266ad]/30 bg-[#3266ad]/5 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: o.color }} />
                  <span className="text-sm font-bold" style={{ color: o.color }}>{o.type}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 font-semibold ml-2">{o.zoning}</span>
                </div>
                <p className="text-[12px] text-[var(--color-text-secondary)]">{o.flow}</p>
                <p className="text-[10px] text-[var(--color-text-muted)] mt-1">전파 딜레이: {o.delay}</p>
              </div>
            ))}
          </div>

          {/* Archived origins — 접이식 */}
          {HYPOTHESIS.archived && (
            <details className="text-[11px]">
              <summary className="text-[var(--color-text-muted)] cursor-pointer hover:text-[var(--color-text-secondary)] mb-2">
                기타 Origin 타입 (참고용) ▸
              </summary>
              <div className="grid grid-cols-3 gap-2 opacity-60">
                {HYPOTHESIS.archived.map((o) => (
                  <div key={o.type} className="border border-[var(--color-border)] rounded-lg p-3">
                    <div className="flex items-center gap-1.5 mb-1">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: o.color }} />
                      <span className="text-[11px] font-semibold" style={{ color: o.color }}>{o.type}</span>
                    </div>
                    <p className="text-[10px] text-[var(--color-text-muted)]">{o.flow}</p>
                    <p className="text-[9px] text-[var(--color-text-muted)] mt-1 italic">{o.note}</p>
                  </div>
                ))}
              </div>
            </details>
          )}
        </section>

        {/* Verification Progress */}
        <section className="mb-10">
          <h2 className="font-['Lora'] text-lg font-semibold mb-4">검증 진행 상황</h2>
          <div className="flex gap-0">
            {VERIFICATION.map((v, i) => (
              <div key={v.step} className="flex-1 relative">
                {i < VERIFICATION.length - 1 && (
                  <div className={`absolute top-4 left-[calc(50%+16px)] right-0 h-0.5 ${
                    v.status === "done" ? "bg-emerald-300" : "bg-gray-200"
                  }`} />
                )}
                <div className="flex flex-col items-center text-center px-2">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold mb-2 ${
                    v.status === "done" ? "bg-emerald-500 text-white" :
                    v.status === "active" ? "bg-blue-500 text-white" :
                    "bg-gray-200 text-gray-500"
                  }`}>
                    {v.status === "done" ? "✓" : v.step}
                  </div>
                  <div className="text-[11px] font-semibold text-[var(--color-text)]">{v.title}</div>
                  <Badge status={v.status} />
                  <div className="text-[10px] text-[var(--color-text-muted)] mt-1 leading-tight">{v.detail}</div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* AI Insights Report */}
        <section className="mb-10">
          <h2 className="font-['Lora'] text-lg font-semibold mb-4">{AI_INSIGHTS.title}</h2>

          {/* Test Results — 3 Column Cards */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            {AI_INSIGHTS.sections.map((s) => (
              <div key={s.label} className="border border-[var(--color-border)] rounded-lg overflow-hidden bg-white flex flex-col">
                <div className="px-4 py-3 flex items-center gap-2" style={{ backgroundColor: s.color + "10", borderBottom: `2px solid ${s.color}` }}>
                  <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: s.color }} />
                  <span className="text-sm font-bold" style={{ color: s.color }}>{s.label}</span>
                  <span className="ml-auto"><Badge status={s.status} /></span>
                </div>
                <div className="px-4 py-4 flex-1 flex flex-col gap-3">
                  <div>
                    <div className="text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-1">발견</div>
                    <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">{s.finding}</p>
                  </div>
                  <div className="mt-auto pt-3 border-t border-[var(--color-border)]/50">
                    <div className="text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-1">한계</div>
                    <p className="text-[11px] text-[var(--color-text-muted)] italic leading-relaxed">{s.limitation}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Conclusion */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-xs text-blue-800 mb-4">
            <strong>결론:</strong> {AI_INSIGHTS.conclusion}
          </div>

          {/* Next Steps */}
          <div className="bg-white border border-[var(--color-border)] rounded-lg p-4">
            <h3 className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-3">다음 검증 단계</h3>
            <div className="space-y-2">
              {AI_INSIGHTS.nextSteps.map((ns, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5 ${
                    ns.status === "active" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-500"
                  }`}>{i + 1}</div>
                  <div>
                    <div className="text-xs font-semibold text-[var(--color-text)]">{ns.step}</div>
                    <div className="text-[11px] text-[var(--color-text-secondary)]">{ns.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Pages */}
        <section className="mb-10">
          <h2 className="font-['Lora'] text-lg font-semibold mb-4">대시보드 페이지</h2>
          <div className="grid grid-cols-2 gap-3">
            {PAGES.map((p) => (
              <a
                key={p.path}
                href={p.path}
                className={`block rounded-lg p-4 transition-all ${
                  p.highlight
                    ? "border-2 border-[var(--color-primary)]/40 bg-[var(--color-primary)]/[0.02] hover:border-[var(--color-primary)] hover:shadow-md"
                    : "border border-[var(--color-border)] hover:border-[var(--color-primary)]/30 hover:shadow-sm"
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-sm ${p.highlight ? "font-bold text-[var(--color-text)]" : "font-semibold text-[var(--color-text-secondary)]"}`}>
                    {p.name}
                  </span>
                  <Badge status={p.status} />
                  <span className="text-[10px] text-[var(--color-text-muted)] ml-auto font-mono">{p.path}</span>
                </div>
                <p className="text-[11px] text-[var(--color-text-secondary)] mb-2">{p.description}</p>
                <div className="flex flex-wrap gap-1">
                  {p.features.map((f) => (
                    <span key={f} className="text-[9px] px-1.5 py-0.5 rounded bg-gray-100 text-[var(--color-text-muted)]">
                      {f}
                    </span>
                  ))}
                </div>
              </a>
            ))}
          </div>
        </section>

        {/* Timeline */}
        <section className="mb-10">
          <h2 className="font-['Lora'] text-lg font-semibold mb-4">프로젝트 타임라인</h2>
          <div className="space-y-3">
            {TIMELINE.map((t) => (
              <div
                key={t.phase}
                className={`border rounded-lg p-4 ${
                  t.status === "active"
                    ? "border-[var(--color-primary)]/30 bg-[var(--color-primary)]/[0.02]"
                    : "border-[var(--color-border)]"
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-xs font-bold text-[var(--color-text-muted)] w-[65px]">{t.phase}</span>
                  <span className="text-xs text-[var(--color-text-secondary)] font-mono">{t.period}</span>
                  <span className="text-xs font-semibold text-[var(--color-text)]">{t.label}</span>
                  <div className="ml-auto"><Badge status={t.status} /></div>
                </div>
                <div className="flex flex-wrap gap-x-4 gap-y-1 ml-[65px]">
                  {t.items.map((item) => (
                    <span key={item} className="text-[11px] text-[var(--color-text-secondary)] flex items-center gap-1">
                      <span className={`w-1.5 h-1.5 rounded-full ${
                        t.status === "done" ? "bg-emerald-400" :
                        t.status === "active" ? "bg-blue-400" : "bg-gray-300"
                      }`} />
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <div className="h-8" />
      </div>
    </main>
  );
}
