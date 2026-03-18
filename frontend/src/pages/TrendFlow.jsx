import { useState, useEffect } from "react";

/* ── Color Constants ── */
const ORIGIN_COLORS = {
  runway: "#3266ad",
  capital: "#8B5CF6",
  viral: "#D97706",
  organic: "#059669",
};

const ORIGIN_LABELS = {
  runway: "Runway-led",
  capital: "Capital-driven",
  viral: "Viral / Meme",
  organic: "Market-organic",
};

/* ── Static Data — 2행 배치 (위: 주요 흐름, 아래: 보조 채널) ── */
const flowData = {
  runway: {
    nodes: [
      { id: "runway", x: 40, y: 50, w: 120, label: "런웨이 컬렉션", active: true },
      { id: "expert", x: 210, y: 50, w: 120, label: "전문가 리포트", active: true },
      { id: "celeb", x: 380, y: 50, w: 110, label: "셀럽 착용", active: true },
      { id: "search", x: 380, y: 130, w: 110, label: "검색량 상승", active: true },
      { id: "market", x: 540, y: 50, w: 110, label: "마켓 등장", active: true },
      { id: "social", x: 210, y: 130, w: 110, label: "소셜 멘션", skip: true },
      { id: "campaign", x: 40, y: 130, w: 120, label: "캠페인 런칭", skip: true },
    ],
    // runway→expert→celeb→market (상단), celeb→search→market (하단 분기)
    edges: [[0,1],[1,2],[2,4],[2,3],[3,4]],
    desc: "Runway-led",
    descText: "런웨이에서 시작하여 전문가→셀럽→마켓 순으로 전파. 시그널이 순차적으로 나타나므로 FTIB가 가장 정확하게 추적 가능. 럭셔리/하이엔드에서 지배적. 전파 딜레이: 평균 6~12개월.",
  },
  capital: {
    nodes: [
      { id: "runway", x: 40, y: 50, w: 120, label: "런웨이 컬렉션", skip: true },
      { id: "expert", x: 210, y: 50, w: 120, label: "전문가 리포트", skip: true },
      { id: "celeb", x: 380, y: 50, w: 130, label: "앰배서더 캠페인", active: true },
      { id: "search", x: 380, y: 130, w: 110, label: "검색량 폭발", active: true },
      { id: "market", x: 540, y: 90, w: 110, label: "마켓 빠른반영", active: true },
      { id: "brand", x: 40, y: 130, w: 130, label: "브랜드 투자 결정", active: true },
    ],
    // brand→celeb (좌하→우상), celeb→search (우상→우하), celeb→market, search→market
    edges: [[5,2],[2,3],[2,4],[3,4]],
    desc: "Capital-driven",
    descText: "브랜드가 셀럽 앰배서더/광고에 투자하여 의도적으로 확산. 런웨이·전문가 단계를 건너뜀. 캠페인 시점에 검색량 급등. FTIB에서는 \"셀럽이름+브랜드\" 검색량 조합으로 감지 가능.",
  },
  viral: {
    nodes: [
      { id: "runway", x: 40, y: 50, w: 120, label: "런웨이 컬렉션", skip: true },
      { id: "expert", x: 210, y: 50, w: 120, label: "전문가 리포트", skip: true },
      { id: "celeb", x: 380, y: 50, w: 110, label: "셀럽 착용", skip: true },
      { id: "search", x: 380, y: 130, w: 110, label: "검색량 급등", active: true },
      { id: "market", x: 540, y: 90, w: 110, label: "마켓 빠른소진", active: true },
      { id: "social", x: 40, y: 130, w: 130, label: "소셜 밈 발생", active: true },
      { id: "tiktok", x: 210, y: 130, w: 120, label: "틱톡/릴스 확산", active: true },
    ],
    // social→tiktok→search→market
    edges: [[5,6],[6,3],[3,4]],
    desc: "Viral / Meme",
    descText: "소셜미디어에서 자연발생한 밈으로 예측 불가하게 확산. 런웨이·전문가·셀럽 시그널이 모두 부재하거나 후행. FTIB에서는 소셜 멘션 모니터링 추가 시 감지 가능. 빠르지만 단명하는 패턴.",
  },
  organic: {
    nodes: [
      { id: "runway", x: 40, y: 50, w: 120, label: "런웨이 컬렉션", skip: true },
      { id: "expert", x: 210, y: 50, w: 120, label: "전문가 리포트", skip: true },
      { id: "celeb", x: 380, y: 50, w: 110, label: "셀럽 착용", skip: true },
      { id: "demand", x: 40, y: 130, w: 130, label: "소비자 실수요", active: true },
      { id: "market", x: 270, y: 130, w: 140, label: "마켓 점진적 확대", active: true },
      { id: "search", x: 490, y: 130, w: 140, label: "검색량 완만상승", active: true },
    ],
    // demand→market→search (하단 좌→우 흐름, 겹침 없음)
    edges: [[3,4],[4,5]],
    desc: "Market-organic",
    descText: "선행 시그널 없이 소비자 수요에서 자연스럽게 성장. 기능성 소재나 실용적 카테고리에서 자주 나타남. FTIB에서는 반복 크롤링으로 상품 수 점진 증가를 감지. 스포츠/아웃도어에서 가장 지배적.",
  },
};

const zoneData = [
  {
    name: "럭셔리 / 하이엔드",
    shortDesc: "Lemaire, Prada, Chanel 등\n런웨이 직접 반영",
    dist: [60, 25, 10, 5],
    descTitle: "럭셔리 / 하이엔드",
    descText: "Runway-led 60%로 지배적. 런웨이 시그널이 가장 직접적으로 반영되며, 같은 시즌 내에 마켓 등장. Capital-driven(앰배서더)이 25%로 보조. FTIB 핵심 추적 영역.",
    monitorPoint: "런웨이 태그 → WGSN/Tagwalk 교차 → 마켓 매칭. 풀 A 키워드 위주 추적.",
  },
  {
    name: "스포츠 / 아웃도어",
    shortDesc: "Nike, Descente, NorthFace\n기획 리드타임 김",
    dist: [15, 30, 15, 40],
    descTitle: "스포츠 / 아웃도어",
    descText: "Market-organic 40%로 지배적. 기능성·실용성 수요가 자체적으로 성장. Capital-driven(선수/모델 앰배서더) 30%. 기획 리드타임이 길어 런웨이 영향은 간접적(15%).",
    monitorPoint: "마켓 상품 수 점진 변화 + 앰배서더 캠페인 감지. 반복 크롤링이 핵심.",
  },
  {
    name: "캐주얼 / 스트리트",
    shortDesc: "MLB, Youth, Marithe\n빠른 사이클",
    dist: [20, 30, 35, 15],
    descTitle: "캐주얼 / 스트리트",
    descText: "Viral/Meme 35%와 Capital-driven 30%가 지배적. SNS 밈에서 시작되는 트렌드가 많고, 셀럽 착용 효과가 큼. 사이클이 빨라 Runway-led는 20%에 불과.",
    monitorPoint: "소셜 멘션 + 셀럽 검색량 스파이크가 핵심 시그널. 틱톡/인스타 해시태그 추적 필요.",
  },
  {
    name: "SPA / 매스",
    shortDesc: "Zara, H&M, 무신사\n모든 Origin 팔로우",
    dist: [25, 20, 30, 25],
    descTitle: "SPA / 매스",
    descText: "모든 Origin을 빠르게 팔로우(각 20~30%). 반응 속도가 핵심 — Zara는 2~4개월 내 런웨이 트렌드를 상품화. 무신사 입점 브랜드도 유사 패턴.",
    monitorPoint: "4가지 Origin 시그널 중 어느 것이든 감지되면 마켓 반영까지 가장 짧은 딜레이. 마켓 반복 크롤링으로 \"누가 먼저 반영했는가\" 추적.",
  },
];

const timelineData = {
  runway: {
    label: "Runway-led",
    rows: [
      { label: "런웨이", left: 0, width: 8, opacity: 1, text: "●" },
      { label: "전문가", left: 5, width: 15, opacity: 0.7, text: "리포트" },
      { label: "셀럽", left: 25, width: 20, opacity: 0.55, text: "착용" },
      { label: "검색량", left: 30, width: 35, opacity: 0.4, text: "상승" },
      { label: "마켓", left: 40, width: 45, opacity: 0.3, text: "상품 등장" },
    ],
  },
  capital: {
    label: "Capital-driven",
    rows: [
      { label: "런웨이", left: 0, width: 5, opacity: 0.2, text: "약" },
      { label: "전문가", left: 5, width: 8, opacity: 0.2, text: "약" },
      { label: "캠페인", left: 20, width: 10, opacity: 1, text: "런칭!" },
      { label: "검색량", left: 22, width: 30, opacity: 0.6, text: "폭발" },
      { label: "마켓", left: 25, width: 40, opacity: 0.35, text: "빠른 반영" },
    ],
  },
  viral: {
    label: "Viral / Meme",
    rows: [
      { label: "런웨이", left: 0, width: 3, opacity: 0.15, text: "—" },
      { label: "전문가", left: 0, width: 3, opacity: 0.15, text: "—" },
      { label: "소셜", left: 35, width: 12, opacity: 1, text: "밈 발생!" },
      { label: "검색량", left: 40, width: 20, opacity: 0.6, text: "급등" },
      { label: "마켓", left: 45, width: 25, opacity: 0.35, text: "빠른 소진" },
    ],
  },
  organic: {
    label: "Market-organic",
    rows: [
      { label: "런웨이", left: 0, width: 3, opacity: 0.15, text: "—" },
      { label: "전문가", left: 0, width: 3, opacity: 0.15, text: "—" },
      { label: "검색량", left: 10, width: 70, opacity: 0.25, text: "완만한 상승" },
      { label: "마켓", left: 5, width: 80, opacity: 0.35, text: "점진적 확대" },
    ],
  },
};

/* ── Tab 0: 2행 배치 Flow Diagram (이전 레이아웃 + 깔끔한 화살표) ── */
function FlowDiagram({ origin }) {
  const data = flowData[origin];
  const color = ORIGIN_COLORS[origin];
  const [visible, setVisible] = useState(false);
  const nodeH = 36;

  useEffect(() => {
    setVisible(false);
    const t = setTimeout(() => setVisible(true), 50);
    return () => clearTimeout(t);
  }, [origin]);

  // 두 노드 간 연결점 계산
  function getEdgePath(from, to) {
    const fCx = from.x + from.w / 2;
    const fCy = from.y + nodeH / 2;
    const tCx = to.x + to.w / 2;
    const tCy = to.y + nodeH / 2;
    const fR = from.x + from.w;
    const tL = to.x;

    // 같은 행, 좌→우: 오른쪽 중심 → 왼쪽 중심
    if (Math.abs(fCy - tCy) < 20 && fR < tL) {
      return `M${fR},${fCy} L${tL},${tCy}`;
    }
    // 위→아래 (같은 열 근처): 하단 중심 → 상단 중심, 부드러운 S커브
    if (tCy > fCy && Math.abs(fCx - tCx) < from.w) {
      return `M${fCx},${from.y + nodeH} C${fCx},${from.y + nodeH + 25} ${tCx},${to.y - 25} ${tCx},${to.y}`;
    }
    // 좌하→우상 대각선: 부드러운 베지어
    if (fCy > tCy) {
      return `M${fR},${fCy} C${fR + 30},${fCy} ${tL - 30},${tCy} ${tL},${tCy}`;
    }
    // 우상→좌하 (역방향): 오른쪽 하단 → 왼쪽 상단
    if (tCx < fCx) {
      return `M${fCx},${from.y + nodeH} C${fCx},${from.y + nodeH + 40} ${tCx + to.w},${tCy} ${to.x + to.w},${tCy}`;
    }
    // 기본: 대각선 베지어
    return `M${fR},${fCy} C${fR + 40},${fCy} ${tL - 40},${tCy} ${tL},${tCy}`;
  }

  return (
    <svg
      width="100%"
      viewBox="0 0 700 210"
      className="my-4"
      style={{ transition: "opacity 0.3s", opacity: visible ? 1 : 0 }}
    >
      <defs>
        <marker
          id={`arrow-${origin}`}
          viewBox="0 0 10 10"
          refX="9"
          refY="5"
          markerWidth="7"
          markerHeight="7"
          orient="auto-start-reverse"
        >
          <path d="M1 1.5L7.5 5L1 8.5" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </marker>
      </defs>

      {/* Edges */}
      {data.edges.map(([fromIdx, toIdx], i) => {
        const from = data.nodes[fromIdx];
        const to = data.nodes[toIdx];
        const pathD = getEdgePath(from, to);
        return (
          <path
            key={`edge-${i}`}
            d={pathD}
            stroke={color}
            strokeWidth="1.5"
            fill="none"
            markerEnd={`url(#arrow-${origin})`}
            opacity={visible ? 0.55 : 0}
            style={{ transition: `opacity 0.4s ease ${0.1 + i * 0.12}s` }}
          />
        );
      })}

      {/* Nodes */}
      {data.nodes.map((n, i) => (
        <g
          key={n.id}
          opacity={visible ? (n.skip ? 0.25 : 1) : 0}
          style={{ transition: `opacity 0.4s ease ${0.05 + i * 0.08}s` }}
        >
          <rect
            x={n.x}
            y={n.y}
            width={n.w}
            height={nodeH}
            rx={8}
            fill={n.skip ? "rgba(128,128,128,0.04)" : `${color}12`}
            stroke={n.skip ? "rgba(128,128,128,0.2)" : color}
            strokeWidth={n.skip ? "0.5" : "1"}
            strokeDasharray={n.skip ? "4 3" : undefined}
          />
          <text
            x={n.x + n.w / 2}
            y={n.y + nodeH / 2}
            textAnchor="middle"
            dominantBaseline="central"
            fontSize="12"
            fontWeight="500"
            fill={n.skip ? "rgba(128,128,128,0.45)" : "var(--color-text-secondary)"}
            style={{ fontFamily: "var(--font-sans, system-ui)" }}
          >
            {n.label}
          </text>
        </g>
      ))}
    </svg>
  );
}

/* ── Tab 1: Zone Cards ── */
function OriginBar({ dist }) {
  const colors = [ORIGIN_COLORS.runway, ORIGIN_COLORS.capital, ORIGIN_COLORS.viral, ORIGIN_COLORS.organic];
  return (
    <div className="flex h-2 rounded-full overflow-hidden mt-3 bg-[var(--color-bg)]">
      {dist.map((pct, i) => (
        <div
          key={i}
          className="h-full transition-all duration-400"
          style={{ width: `${pct}%`, backgroundColor: colors[i] }}
        />
      ))}
    </div>
  );
}

function OriginLegend() {
  const origins = ["runway", "capital", "viral", "organic"];
  return (
    <div className="flex gap-4 mt-4 flex-wrap">
      {origins.map((key) => (
        <span key={key} className="flex items-center gap-1.5 text-[11px] text-[var(--color-text-secondary)]">
          <span
            className="w-2.5 h-2.5 rounded-sm inline-block"
            style={{ backgroundColor: ORIGIN_COLORS[key] }}
          />
          {ORIGIN_LABELS[key]}
        </span>
      ))}
    </div>
  );
}

/* ── Tab 2: Timeline ── */
function TimelineSection({ originKey, isLast }) {
  const data = timelineData[originKey];
  const color = ORIGIN_COLORS[originKey];

  return (
    <div className={`pb-5 ${!isLast ? "mb-5 border-b border-[var(--color-border)]" : ""}`}>
      <div className="text-sm font-semibold mt-2 mb-3 flex items-center gap-2" style={{ color }}>
        <span className="w-3 h-3 rounded-sm inline-block" style={{ backgroundColor: color }} />
        {data.label}
      </div>
      {data.rows.map((row, i) => (
        <div key={i} className="flex items-center gap-0 my-1.5 relative">
          <div className="w-[100px] text-xs text-[var(--color-text-secondary)] shrink-0 font-medium">
            {row.label}
          </div>
          <div className="flex-1 h-7 relative bg-[var(--color-surface)] rounded overflow-hidden">
            <div
              className="absolute h-full rounded flex items-center px-2 text-[10px] font-medium text-white whitespace-nowrap transition-all duration-500"
              style={{
                left: `${row.left}%`,
                width: `${row.width}%`,
                backgroundColor: color,
                opacity: row.opacity,
              }}
            >
              {row.text}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ── Main Page ── */
export default function TrendFlow() {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedOrigin, setSelectedOrigin] = useState("runway");
  const [selectedZone, setSelectedZone] = useState(0);

  const tabs = [
    "Origin별 시그널 플로우",
    "조닝별 Origin 분포",
    "통합 타임라인 비교",
  ];

  return (
    <main className="flex-1 flex flex-col overflow-hidden bg-[var(--color-bg)]">
      {/* Sticky Header + Tabs */}
      <div className="shrink-0 bg-[var(--color-bg)] border-b border-[var(--color-border)] px-8 pt-6">
        <div className="max-w-[1100px] mx-auto">
          <h1 className="font-['Lora'] text-xl font-semibold tracking-wide mb-1">
            Trend Origin Flow Framework
          </h1>
          <p className="text-sm text-[var(--color-text-secondary)] mb-4">
            트렌드가 어디에서 시작되어 어떤 경로로 전파되는지 분석하는 프레임워크
          </p>

          <div className="flex gap-0">
            {tabs.map((label, i) => (
              <button
                key={i}
                onClick={() => setActiveTab(i)}
                className={`px-5 py-2.5 text-[13px] font-medium border-b-2 transition-all bg-transparent ${
                  activeTab === i
                    ? "text-[var(--color-primary)] border-[var(--color-primary)]"
                    : "text-[var(--color-text-secondary)] border-transparent hover:text-[var(--color-text-secondary)]"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
      <div className="max-w-[1100px] mx-auto">
        {/* Tab 0: Origin Flow Patterns */}
        {activeTab === 0 && (
          <div>
            <div className="flex gap-2 mb-3">
              {Object.keys(ORIGIN_LABELS).map((key) => (
                <button
                  key={key}
                  onClick={() => setSelectedOrigin(key)}
                  className={`px-3.5 py-1.5 text-xs rounded-md border transition-all ${
                    selectedOrigin === key
                      ? "border-[var(--color-primary)] bg-[var(--color-primary)]/8 text-[var(--color-primary)] font-medium"
                      : "border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)]"
                  }`}
                >
                  {ORIGIN_LABELS[key]}
                </button>
              ))}
            </div>

            <FlowDiagram origin={selectedOrigin} />

            <div className="mt-4 p-4 bg-[var(--color-surface)] rounded-md text-xs leading-relaxed text-[var(--color-text-secondary)]">
              <strong className="text-[var(--color-text-secondary)] font-medium">
                {flowData[selectedOrigin].desc}
              </strong>
              {" — "}
              {flowData[selectedOrigin].descText}
            </div>
          </div>
        )}

        {/* Tab 1: Zone Distribution — 2×2 */}
        {activeTab === 1 && (
          <div>
            <div className="grid grid-cols-2 gap-4 mb-4">
              {zoneData.map((zone, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedZone(i)}
                  className={`text-left p-5 rounded-lg border transition-all ${
                    selectedZone === i
                      ? "border-[var(--color-primary)] bg-[var(--color-primary)]/5"
                      : "border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-primary)]/30"
                  }`}
                >
                  <div className="text-sm font-semibold mb-2">{zone.name}</div>
                  <div className="text-xs text-[var(--color-text-secondary)] leading-relaxed whitespace-pre-line mb-1">
                    {zone.shortDesc}
                  </div>
                  <OriginBar dist={zone.dist} />
                  <div className="flex gap-3 mt-2">
                    {zone.dist.map((pct, j) => (
                      <span key={j} className="text-[10px] text-[var(--color-text-muted)]">
                        {["R", "C", "V", "O"][j]} {pct}%
                      </span>
                    ))}
                  </div>
                </button>
              ))}
            </div>

            <OriginLegend />

            <div className="mt-4 p-4 bg-[var(--color-surface)] rounded-md text-xs leading-relaxed text-[var(--color-text-secondary)]">
              <strong className="text-[var(--color-text-secondary)] font-medium">
                {zoneData[selectedZone].descTitle}
              </strong>
              {" — "}
              {zoneData[selectedZone].descText}
              <br /><br />
              <strong className="text-[var(--color-text-secondary)] font-medium">
                모니터링 포인트:
              </strong>
              {" "}
              {zoneData[selectedZone].monitorPoint}
            </div>
          </div>
        )}

        {/* Tab 2: Timeline Comparison */}
        {activeTab === 2 && (
          <div>
            <div className="text-sm font-medium mb-3">
              Origin별 시그널 발생 타이밍 비교
            </div>

            <div className="flex items-center gap-0 mb-1 ml-[100px]">
              <div className="flex-1 flex justify-between text-[10px] text-[var(--color-text-muted)] font-mono">
                <span>런웨이 쇼</span>
                <span>+2개월</span>
                <span>+4개월</span>
                <span>+6개월</span>
                <span>+9개월</span>
                <span>+12개월</span>
              </div>
            </div>

            {["runway", "capital", "viral", "organic"].map((key, i) => (
              <TimelineSection key={key} originKey={key} isLast={i === 3} />
            ))}

            <div className="mt-4 p-3 bg-[var(--color-surface)] rounded-md text-xs leading-relaxed text-[var(--color-text-secondary)]">
              <strong className="text-[var(--color-text-secondary)] font-medium">
                핵심 관찰:
              </strong>
              {" "}
              Runway-led는 시그널이 순차적으로 나타나 예측 가능. Capital-driven은 캠페인 시점에 급등. Viral은 예측 불가하지만 소셜→검색 순서가 명확. Market-organic은 선행 시그널 없이 점진적 — FTIB의 반복 크롤링으로 감지 가능.
            </div>
          </div>
        )}

        <div className="h-8" />
      </div>
      </div>
    </main>
  );
}
