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

/* ── Static Data ── */
const flowData = {
  runway: {
    nodes: [
      { id: "runway", x: 40, y: 60, w: 120, label: "런웨이 컬렉션", active: true },
      { id: "expert", x: 200, y: 60, w: 110, label: "전문가 리포트", active: true },
      { id: "celeb", x: 350, y: 60, w: 110, label: "셀럽 착용", active: true },
      { id: "search", x: 350, y: 140, w: 100, label: "검색량 상승", active: true },
      { id: "market", x: 520, y: 60, w: 110, label: "마켓 등장", active: true },
      { id: "social", x: 200, y: 140, w: 100, label: "소셜 멘션", skip: true },
      { id: "campaign", x: 40, y: 140, w: 110, label: "캠페인 런칭", skip: true },
    ],
    edges: [[0, 1], [1, 2], [2, 4], [2, 3], [3, 4]],
    timeLabels: ["T+0", "T+1~2M", "T+3~6M", "T+6~12M"],
    timeXs: [60, 230, 380, 550],
    desc: "Runway-led",
    descText: "런웨이에서 시작하여 전문가→셀럽→마켓 순으로 전파. 시그널이 순차적으로 나타나므로 FTIB가 가장 정확하게 추적 가능. 럭셔리/하이엔드에서 지배적. 전파 딜레이: 평균 6~12개월.",
  },
  capital: {
    nodes: [
      { id: "runway", x: 40, y: 60, w: 120, label: "런웨이 컬렉션", skip: true },
      { id: "expert", x: 200, y: 60, w: 110, label: "전문가 리포트", skip: true },
      { id: "celeb", x: 350, y: 60, w: 130, label: "앰배서더 캠페인", active: true },
      { id: "search", x: 350, y: 140, w: 100, label: "검색량 폭발", active: true },
      { id: "market", x: 520, y: 60, w: 110, label: "마켓 빠른반영", active: true },
      { id: "brand", x: 40, y: 140, w: 130, label: "브랜드 투자 결정", active: true },
    ],
    edges: [[5, 2], [2, 3], [2, 4], [3, 4]],
    timeLabels: ["(약)", "(약)", "캠페인 시점", "T+1~3M"],
    timeXs: [80, 230, 380, 550],
    desc: "Capital-driven",
    descText: "브랜드가 셀럽 앰배서더/광고에 투자하여 의도적으로 확산. 런웨이·전문가 단계를 건너뜀. 캠페인 시점에 검색량 급등. FTIB에서는 \"셀럽이름+브랜드\" 검색량 조합으로 감지 가능.",
  },
  viral: {
    nodes: [
      { id: "runway", x: 40, y: 60, w: 120, label: "런웨이 컬렉션", skip: true },
      { id: "expert", x: 200, y: 60, w: 110, label: "전문가 리포트", skip: true },
      { id: "celeb", x: 350, y: 60, w: 110, label: "셀럽 착용", skip: true },
      { id: "search", x: 350, y: 140, w: 100, label: "검색량 급등", active: true },
      { id: "market", x: 520, y: 60, w: 110, label: "마켓 빠른소진", active: true },
      { id: "social", x: 40, y: 140, w: 130, label: "소셜 밈 발생", active: true },
      { id: "tiktok", x: 200, y: 140, w: 100, label: "틱톡/릴스 확산", active: true },
    ],
    edges: [[5, 6], [6, 3], [3, 4]],
    timeLabels: ["(없음)", "(없음)", "밈 발생!", "T+1~4주"],
    timeXs: [80, 230, 100, 550],
    desc: "Viral / Meme",
    descText: "소셜미디어에서 자연발생한 밈으로 예측 불가하게 확산. 런웨이·전문가·셀럽 시그널이 모두 부재하거나 후행. FTIB에서는 소셜 멘션 모니터링 추가 시 감지 가능. 빠르지만 단명하는 패턴.",
  },
  organic: {
    nodes: [
      { id: "runway", x: 40, y: 60, w: 120, label: "런웨이 컬렉션", skip: true },
      { id: "expert", x: 200, y: 60, w: 110, label: "전문가 리포트", skip: true },
      { id: "celeb", x: 350, y: 60, w: 110, label: "셀럽 착용", skip: true },
      { id: "search", x: 200, y: 140, w: 120, label: "검색량 완만상승", active: true },
      { id: "market", x: 40, y: 140, w: 130, label: "마켓 점진적 확대", active: true },
      { id: "demand", x: 520, y: 60, w: 110, label: "소비자 실수요", active: true },
    ],
    edges: [[4, 3], [5, 4]],
    timeLabels: ["(없음)", "(없음)", "점진적", "지속 성장"],
    timeXs: [80, 230, 230, 550],
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
      { label: "런웨이", left: 0, width: 8, opacity: 1, text: "\u25CF" },
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
      { label: "런웨이", left: 0, width: 3, opacity: 0.15, text: "\u2014" },
      { label: "전문가", left: 0, width: 3, opacity: 0.15, text: "\u2014" },
      { label: "소셜", left: 35, width: 12, opacity: 1, text: "밈 발생!" },
      { label: "검색량", left: 40, width: 20, opacity: 0.6, text: "급등" },
      { label: "마켓", left: 45, width: 25, opacity: 0.35, text: "빠른 소진" },
    ],
  },
  organic: {
    label: "Market-organic",
    rows: [
      { label: "런웨이", left: 0, width: 3, opacity: 0.15, text: "\u2014" },
      { label: "전문가", left: 0, width: 3, opacity: 0.15, text: "\u2014" },
      { label: "검색량", left: 10, width: 70, opacity: 0.25, text: "완만한 상승" },
      { label: "마켓", left: 5, width: 80, opacity: 0.35, text: "점진적 확대" },
    ],
  },
};

/* ── Tab 0: SVG Flow Diagram ── */
function FlowDiagram({ origin }) {
  const data = flowData[origin];
  const color = ORIGIN_COLORS[origin];
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(false);
    const t = setTimeout(() => setVisible(true), 50);
    return () => clearTimeout(t);
  }, [origin]);

  return (
    <svg
      width="100%"
      viewBox="0 0 680 280"
      className="my-4"
      style={{ transition: "opacity 0.3s", opacity: visible ? 1 : 0 }}
    >
      <defs>
        <marker
          id={`arrow-${origin}`}
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path
            d="M2 1L8 5L2 9"
            fill="none"
            stroke={color}
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </marker>
      </defs>

      {/* Edges */}
      {data.edges.map(([fromIdx, toIdx], i) => {
        const from = data.nodes[fromIdx];
        const to = data.nodes[toIdx];

        // Check if nodes overlap horizontally (vertical connection)
        const fromRight = from.x + from.w;
        const toRight = to.x + to.w;
        const hOverlap = from.x < toRight && to.x < fromRight;
        // Check if target is far to the left (backward connection)
        const isBackward = to.x + to.w < from.x - 40;

        let pathD;
        if (hOverlap && to.y > from.y) {
          // Vertical: go from bottom-center of source, curve right, to top-center of target
          const x1 = from.x + from.w / 2 + 20;
          const y1 = from.y + 36;
          const x2 = to.x + to.w / 2;
          const y2 = to.y;
          const midX = Math.max(fromRight, toRight) + 30;
          pathD = `M${x1},${y1} C${midX},${y1} ${midX},${y2} ${x2},${y2}`;
        } else if (isBackward) {
          // Backward: curve down from source bottom, sweep left to target right
          const x1 = from.x + from.w / 2;
          const y1 = from.y + 36;
          const x2 = to.x + to.w;
          const y2 = to.y + 18;
          const dropY = Math.max(from.y, to.y) + 70;
          pathD = `M${x1},${y1} C${x1},${dropY} ${x2 + 60},${dropY} ${x2},${y2}`;
        } else {
          // Normal: right-center to left-center
          const x1 = fromRight;
          const y1 = from.y + 18;
          const x2 = to.x;
          const y2 = to.y + 18;
          pathD = `M${x1},${y1} L${x2},${y2}`;
        }

        return (
          <path
            key={`edge-${i}`}
            d={pathD}
            stroke={color}
            strokeWidth="1.5"
            fill="none"
            markerEnd={`url(#arrow-${origin})`}
            opacity={visible ? 0.6 : 0}
            style={{ transition: `opacity 0.4s ease ${0.1 + i * 0.15}s` }}
          />
        );
      })}

      {/* Nodes */}
      {data.nodes.map((n, i) => (
        <g
          key={n.id}
          opacity={visible ? (n.skip ? 0.3 : 1) : 0}
          style={{ transition: `opacity 0.4s ease ${0.05 + i * 0.1}s` }}
        >
          <rect
            x={n.x}
            y={n.y}
            width={n.w}
            height={36}
            rx={6}
            fill={n.skip ? "rgba(128,128,128,0.05)" : `${color}18`}
            stroke={n.skip ? "rgba(128,128,128,0.2)" : color}
            strokeWidth="0.5"
            strokeDasharray={n.skip ? "4 3" : undefined}
          />
          <text
            x={n.x + n.w / 2}
            y={n.y + 18}
            textAnchor="middle"
            dominantBaseline="central"
            fontSize="12"
            fontWeight="500"
            fill={n.skip ? "rgba(128,128,128,0.5)" : "var(--color-text-secondary)"}
            style={{ fontFamily: "var(--font-sans, system-ui)" }}
          >
            {n.label}
          </text>
        </g>
      ))}

      {/* Time Labels */}
      {data.timeLabels.map((label, i) => (
        <text
          key={`tl-${i}`}
          x={data.timeXs[i]}
          y={240}
          fontSize="10"
          fill="rgba(128,128,128,0.5)"
          style={{ fontFamily: "var(--font-mono, monospace)" }}
        >
          {label}
        </text>
      ))}
    </svg>
  );
}

/* ── Tab 1: Zone Cards ── */
function OriginBar({ dist }) {
  const colors = [ORIGIN_COLORS.runway, ORIGIN_COLORS.capital, ORIGIN_COLORS.viral, ORIGIN_COLORS.organic];
  return (
    <div className="flex h-1.5 rounded-full overflow-hidden mt-2.5 bg-[var(--color-bg)]">
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
    <div className="flex gap-4 mt-3 flex-wrap">
      {origins.map((key) => (
        <span key={key} className="flex items-center gap-1.5 text-[11px] text-[var(--color-text-secondary)]">
          <span
            className="w-2 h-2 rounded-sm inline-block"
            style={{ backgroundColor: ORIGIN_COLORS[key] }}
          />
          {ORIGIN_LABELS[key]}
        </span>
      ))}
    </div>
  );
}

/* ── Tab 2: Timeline ── */
function TimelineSection({ originKey }) {
  const data = timelineData[originKey];
  const color = ORIGIN_COLORS[originKey];

  return (
    <div className="mb-4">
      <div className="text-xs font-medium mt-4 mb-2" style={{ color }}>
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
    <main className="flex-1 overflow-y-auto bg-[var(--color-bg)]">
      <div className="max-w-[1100px] mx-auto px-8 py-6">
        <h1 className="font-['Lora'] text-xl font-semibold tracking-wide mb-1">
          Trend Origin Flow Framework
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)] mb-6">
          트렌드가 어디에서 시작되어 어떤 경로로 전파되는지 분석하는 프레임워크
        </p>

        {/* Tabs */}
        <div className="flex gap-0 border-b border-[var(--color-border)] mb-6">
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

        {/* Tab 0: Origin Flow Patterns */}
        {activeTab === 0 && (
          <div>
            {/* Origin selector buttons */}
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

            {/* SVG Flow Diagram */}
            <FlowDiagram origin={selectedOrigin} />

            {/* Description */}
            <div className="mt-4 p-4 bg-[var(--color-surface)] rounded-md text-xs leading-relaxed text-[var(--color-text-secondary)]">
              <strong className="text-[var(--color-text-secondary)] font-medium">
                {flowData[selectedOrigin].desc}
              </strong>
              {" \u2014 "}
              {flowData[selectedOrigin].descText}
            </div>
          </div>
        )}

        {/* Tab 1: Zone Distribution */}
        {activeTab === 1 && (
          <div>
            {/* Zone cards grid */}
            <div className="grid grid-cols-4 gap-3 mb-4">
              {zoneData.map((zone, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedZone(i)}
                  className={`text-left p-4 rounded-md border transition-all ${
                    selectedZone === i
                      ? "border-[var(--color-primary)] bg-[var(--color-primary)]/5"
                      : "border-transparent bg-[var(--color-surface)] hover:border-[var(--color-border)]"
                  }`}
                >
                  <div className="text-[13px] font-medium mb-1.5">{zone.name}</div>
                  <div className="text-[11px] text-[var(--color-text-secondary)] leading-relaxed whitespace-pre-line">
                    {zone.shortDesc}
                  </div>
                  <OriginBar dist={zone.dist} />
                </button>
              ))}
            </div>

            <OriginLegend />

            {/* Zone description */}
            <div className="mt-4 p-4 bg-[var(--color-surface)] rounded-md text-xs leading-relaxed text-[var(--color-text-secondary)]">
              <strong className="text-[var(--color-text-secondary)] font-medium">
                {zoneData[selectedZone].descTitle}
              </strong>
              {" \u2014 "}
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

            {/* Timeline axis labels */}
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

            {/* Timeline sections */}
            {["runway", "capital", "viral", "organic"].map((key) => (
              <TimelineSection key={key} originKey={key} />
            ))}

            {/* Key observation note */}
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
    </main>
  );
}
