/* ── 프로젝트 데이터 ── */
const PROJECT = {
  title: "Fashion Trend Intelligence Board",
  subtitle: "패션 트렌드 전파를 데이터 기반으로 추적하는 대시보드",
  version: "v1.0",
  lastUpdate: "2026-03-25",
};

const HYPOTHESIS = {
  core: "런웨이 시그널 → 전문가 리포트 → 셀럽 채택 → 마켓 확산 → 다음 시즌 예측",
  description: "패션 트렌드의 전파 경로를 5단계 파이프라인으로 정량화할 수 있다는 가설을 데이터로 검증합니다.",
  origins: [
    { type: "Runway-led", flow: "런웨이 → 전문가 → 셀럽 → 검색 → 마켓", delay: "6~12개월", color: "#3266ad", zoning: "럭셔리" },
    { type: "Capital-driven", flow: "브랜드 투자 → 캠페인 → 검색 폭발 → 마켓", delay: "1~3개월", color: "#8B5CF6", zoning: "스포츠/캐주얼" },
    { type: "Viral / Meme", flow: "소셜 밈 → 틱톡 확산 → 검색 급등 → 마켓 소진", delay: "1~4주", color: "#D97706", zoning: "스트리트" },
    { type: "Market-organic", flow: "소비자 수요 → 마켓 점진 확대 → 검색 완만 상승", delay: "점진적", color: "#059669", zoning: "아웃도어" },
  ],
};

const DATA_STATS = [
  { label: "마켓 상품", value: "7,542", sub: "28개 브랜드" },
  { label: "런웨이 룩", value: "10,930", sub: "38 디자이너 × 6시즌" },
  { label: "VLM 라벨", value: "10,631", sub: "97.3% 완료" },
  { label: "대시보드", value: "8 pages", sub: "Production 배포" },
];

const PAGES = [
  {
    name: "Runway",
    path: "/runway",
    status: "live",
    highlight: true,
    description: "38명 디자이너의 10,930개 런웨이 룩을 시즌/태그별로 탐색합니다.",
    features: ["디자이너별 룩 그리드", "시즌/태그 필터", "Trend Flow 크로스 링크"],
  },
  {
    name: "Runway VLM Test",
    path: "/vlm",
    status: "beta",
    highlight: true,
    description: "Claude Vision으로 라벨링된 런웨이 룩의 아이템, 실루엣, 컬러, 소재를 시각화합니다.",
    features: ["VLM 라벨 필터링", "아이템별 속성 표시", "10,631개 라벨 완료"],
  },
  {
    name: "Market Brand Board",
    path: "/market",
    status: "live",
    highlight: true,
    description: "28개 브랜드의 마켓 상품을 조닝별로 탐색하고, 런웨이 트렌드 키워드로 필터링합니다.",
    features: ["조닝별 브랜드 하이어라키", "Runway Trend Keywords 칩 필터", "카테고리 8 중분류"],
  },
  {
    name: "Trend Flow",
    path: "/flow",
    status: "live",
    description: "트렌드가 어디에서 시작되어 어떤 경로로 전파되는지 분석하는 Origin 프레임워크입니다.",
    features: ["Origin 4타입 순서도", "조닝별 Origin 분포", "Market-organic 서브타입"],
  },
  {
    name: "Trend Flow check (Test)",
    path: "/flow-check",
    status: "pending",
    description: "VLM + 마켓 매칭 기반 4단계 drill-down 키워드 대시보드. 키워드 체계 정리 후 고도화 예정.",
    features: ["시즌/조닝 필터", "카드/매트릭스/타임라인 뷰", "키워드 표준화 후 재구성 예정"],
  },
  {
    name: "Trend Analysis",
    path: "/trend",
    status: "live",
    description: "마켓 + VLM 데이터 기반의 컬러/소재/실루엣 트렌드 분석입니다.",
    features: ["KPI 카드", "컬러 버블 차트", "브랜드×소재 히트맵"],
  },
  {
    name: "Graph View",
    path: "/graph",
    status: "pending",
    description: "브랜드-소재-컬러-카테고리 관계를 그래프로 시각화. 키워드 체계 정리 후 다양한 관점으로 재구성 예정.",
    features: ["VLM/Market 모드", "노드 관계 탐색", "키워드 표준화 후 고도화 예정"],
  },
];

const KEYWORD_STANDARD = {
  title: "키워드 체계 표준화 (4월 핵심 과제)",
  description: "런웨이, 마켓, 본사 기준의 키워드를 통합하여 일관된 분석 기반을 마련합니다.",
  streams: [
    {
      label: "런웨이 VLM 키워드",
      source: "Claude Vision 자동 라벨링",
      lang: "영문",
      example: "navy, leather, oversized, structured",
      status: "완료 (10,631 라벨)",
      color: "#3266ad",
    },
    {
      label: "마켓 브랜드 키워드",
      source: "크롤링 메타데이터 (상품명, 컬러, 소재)",
      lang: "한글/영문 혼재",
      example: "네이비, 가죽, 오버핏, (19)NVY",
      status: "수집 완료, 정규화 필요",
      color: "#D97706",
    },
    {
      label: "본사 관리 키워드",
      source: "현업 라벨링 기준 (타 팀 협의 필요)",
      lang: "한글 기준",
      example: "네이비, 레더, 오버사이즈, 스트럭처드",
      status: "진행 예정",
      color: "#059669",
    },
  ],
  goal: "3가지 키워드 체계를 동의어 매핑 사전으로 연결 → Trend Flow check, Graph View 등 고도화 기반 마련",
};

const TIMELINE = [
  { phase: "Phase 1", period: "3/11 ~ 3/23", label: "데이터 수집 + VLM", status: "done",
    items: ["28개 브랜드 크롤링 (7,542 상품)", "10,930 런웨이 룩 수집", "VLM 전체 라벨링 완료", "8개 대시보드 페이지 구현 + 배포"] },
  { phase: "Phase 2", period: "3/24 ~ 4/11", label: "전문가 리포트 + 크롤링 확장", status: "active",
    items: ["NotebookLM WGSN 리포트 분석 (시즌 예측 + 디자이너 의도)", "키워드 체계 표준화 (VLM × 마켓 × 본사 기준)", "Hyperbrowser 도입 → WAF 차단 브랜드 재시도", "Tagwalk 프리미엄 리포트 교차 검증"] },
  { phase: "Phase 3", period: "4/14 ~ 4/25", label: "종합 분석", status: "upcoming",
    items: ["전문가 예측 × 런웨이 VLM × 마켓 데이터 상관관계 분석", "Trend Flow / Graph View 키워드 기반 고도화"] },
  { phase: "Phase 4", period: "5월", label: "마켓드리븐 정량화", status: "upcoming",
    items: ["Market-organic 자생 트렌드 정량 지표 설계", "예측 검증 프레임워크 (Pool A/B 사후 검증)"] },
];

const VERIFICATION = [
  { step: "1", title: "런웨이 시그널 수집", status: "done", detail: "10,930 룩, VLM 라벨 10,631개 완료" },
  { step: "2", title: "전문가 리포트 분석", status: "active", detail: "WGSN 4개 리포트 NotebookLM 분석 중" },
  { step: "3", title: "키워드 표준화", status: "active", detail: "VLM × 마켓 × 본사 기준 통합 진행 중" },
  { step: "4", title: "종합 상관관계", status: "upcoming", detail: "4/18 목표 — 전문가×런웨이×마켓 교차" },
  { step: "5", title: "마켓드리븐 정량화", status: "upcoming", detail: "5월 — Market-organic 자생 트렌드 발견" },
];

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
          <div className="grid grid-cols-2 gap-3">
            {HYPOTHESIS.origins.map((o) => (
              <div key={o.type} className="border border-[var(--color-border)] rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: o.color }} />
                  <span className="text-sm font-semibold" style={{ color: o.color }}>{o.type}</span>
                  <span className="text-[10px] text-[var(--color-text-muted)] ml-auto">{o.zoning}</span>
                </div>
                <p className="text-[11px] text-[var(--color-text-secondary)]">{o.flow}</p>
                <p className="text-[10px] text-[var(--color-text-muted)] mt-1">전파 딜레이: {o.delay}</p>
              </div>
            ))}
          </div>
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

        {/* Keyword Standardization — 강조 섹션 */}
        <section className="mb-10">
          <h2 className="font-['Lora'] text-lg font-semibold mb-1">{KEYWORD_STANDARD.title}</h2>
          <p className="text-xs text-[var(--color-text-secondary)] mb-4">{KEYWORD_STANDARD.description}</p>

          <div className="grid grid-cols-3 gap-3 mb-4">
            {KEYWORD_STANDARD.streams.map((s) => (
              <div key={s.label} className="border border-[var(--color-border)] rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: s.color }} />
                  <span className="text-[13px] font-semibold text-[var(--color-text)]">{s.label}</span>
                </div>
                <div className="space-y-1.5 text-[11px]">
                  <div><span className="text-[var(--color-text-muted)]">소스:</span> <span className="text-[var(--color-text-secondary)]">{s.source}</span></div>
                  <div><span className="text-[var(--color-text-muted)]">언어:</span> <span className="text-[var(--color-text-secondary)]">{s.lang}</span></div>
                  <div><span className="text-[var(--color-text-muted)]">예시:</span> <span className="font-mono text-[10px] text-[var(--color-text-secondary)]">{s.example}</span></div>
                  <Badge status={s.status === "완료 (10,631 라벨)" ? "done" : s.status === "진행 예정" ? "upcoming" : "partial"} />
                </div>
              </div>
            ))}
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-xs text-blue-800">
            <strong>목표:</strong> {KEYWORD_STANDARD.goal}
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
