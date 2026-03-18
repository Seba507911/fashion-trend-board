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

/* ── Static Data — 순서도 스타일 (좌→우 흐름) ── */
const flowData = {
  runway: {
    nodes: [
      { id: "runway", label: "런웨이 컬렉션", active: true },
      { id: "expert", label: "전문가 리포트", active: true },
      { id: "celeb", label: "셀럽 착용", active: true },
      { id: "search", label: "검색량 상승", active: true },
      { id: "market", label: "마켓 등장", active: true },
    ],
    edges: [[0,1],[1,2],[2,3],[3,4]],
    skipped: [],
    desc: "Runway-led",
    descText: "런웨이에서 시작하여 전문가→셀럽→검색→마켓 순으로 전파. 시그널이 순차적으로 나타나므로 FTIB가 가장 정확하게 추적 가능. 럭셔리/하이엔드에서 지배적. 전파 딜레이: 평균 6~12개월.",
    timeLabels: ["T+0", "T+1~2M", "T+3~6M", "T+6~9M", "T+9~12M"],
  },
  capital: {
    nodes: [
      { id: "brand", label: "브랜드 투자 결정", active: true },
      { id: "celeb", label: "앰배서더 캠페인", active: true },
      { id: "search", label: "검색량 폭발", active: true },
      { id: "market", label: "마켓 빠른 반영", active: true },
    ],
    edges: [[0,1],[1,2],[1,3],[2,3]],
    skipped: ["런웨이", "전문가"],
    desc: "Capital-driven",
    descText: "브랜드가 셀럽 앰배서더/광고에 투자하여 의도적으로 확산. 런웨이·전문가 단계를 건너뜀. 캠페인 시점에 검색량 급등. FTIB에서는 \"셀럽이름+브랜드\" 검색량 조합으로 감지 가능.",
    timeLabels: ["투자 결정", "캠페인 런칭", "T+1~2M", "T+2~4M"],
  },
  viral: {
    nodes: [
      { id: "social", label: "소셜 밈 발생", active: true },
      { id: "tiktok", label: "틱톡/릴스 확산", active: true },
      { id: "search", label: "검색량 급등", active: true },
      { id: "market", label: "마켓 빠른 소진", active: true },
    ],
    edges: [[0,1],[1,2],[2,3]],
    skipped: ["런웨이", "전문가", "셀럽"],
    desc: "Viral / Meme",
    descText: "소셜미디어에서 자연발생한 밈으로 예측 불가하게 확산. 런웨이·전문가·셀럽 시그널이 모두 부재하거나 후행. FTIB에서는 소셜 멘션 모니터링 추가 시 감지 가능. 빠르지만 단명하는 패턴.",
    timeLabels: ["밈 발생", "1~2주", "T+2~4주", "T+1~2M"],
  },
  organic: {
    nodes: [
      { id: "demand", label: "소비자 실수요", active: true },
      { id: "market", label: "마켓 점진 확대", active: true },
      { id: "search", label: "검색량 완만 상승", active: true },
    ],
    edges: [[0,1],[1,2]],
    skipped: ["런웨이", "전문가", "셀럽"],
    desc: "Market-organic",
    descText: "선행 시그널 없이 소비자 수요에서 자연스럽게 성장. 기능성 소재나 실용적 카테고리에서 자주 나타남. FTIB에서는 반복 크롤링으로 상품 수 점진 증가를 감지. 스포츠/아웃도어에서 가장 지배적.",
    timeLabels: ["지속 수요", "점진 성장", "후행 감지"],
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

/* ── Tab 0: 순서도 스타일 Flow Diagram ── */
function FlowDiagram({ origin }) {
  const data = flowData[origin];
  const color = ORIGIN_COLORS[origin];
  const [visible, setVisible] = useState(false);
  const nodeCount = data.nodes.length;

  useEffect(() => {
    setVisible(false);
    const t = setTimeout(() => setVisible(true), 50);
    return () => clearTimeout(t);
  }, [origin]);

  // 노드를 좌→우 일직선으로 배치
  const nodeW = 130;
  const nodeH = 40;
  const gapX = 40;
  const startX = 30;
  const mainY = 80;
  const totalW = startX + nodeCount * (nodeW + gapX);

  const getNodePos = (idx) => ({
    x: startX + idx * (nodeW + gapX),
    y: mainY,
  });

  return (
    <div className="my-4">
      <svg
        width="100%"
        viewBox={`0 0 ${Math.max(totalW, 680)} 200`}
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
            <path d="M1 1L8 5L1 9" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </marker>
        </defs>

        {/* Edges */}
        {data.edges.map(([fromIdx, toIdx], i) => {
          const from = getNodePos(fromIdx);
          const to = getNodePos(toIdx);
          const isStraight = Math.abs(fromIdx - toIdx) === 1;
          const x1 = from.x + nodeW;
          const y1 = from.y + nodeH / 2;
          const x2 = to.x;
          const y2 = to.y + nodeH / 2;

          let pathD;
          if (isStraight) {
            pathD = `M${x1},${y1} L${x2},${y2}`;
          } else {
            // 분기: 아래로 우회하는 곡선
            const midY = mainY + nodeH + 30;
            pathD = `M${x1},${y1 + 8} C${x1 + 20},${midY} ${x2 - 20},${midY} ${x2},${y2 + 8}`;
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
              style={{ transition: `opacity 0.4s ease ${0.1 + i * 0.12}s` }}
            />
          );
        })}

        {/* Nodes */}
        {data.nodes.map((n, i) => {
          const pos = getNodePos(i);
          return (
            <g
              key={n.id}
              opacity={visible ? 1 : 0}
              style={{ transition: `opacity 0.4s ease ${0.05 + i * 0.1}s` }}
            >
              <rect
                x={pos.x}
                y={pos.y}
                width={nodeW}
                height={nodeH}
                rx={8}
                fill={`${color}15`}
                stroke={color}
                strokeWidth="1"
              />
              <text
                x={pos.x + nodeW / 2}
                y={pos.y + nodeH / 2}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize="12"
                fontWeight="500"
                fill="var(--color-text-secondary)"
                style={{ fontFamily: "var(--font-sans, system-ui)" }}
              >
                {n.label}
              </text>
            </g>
          );
        })}

        {/* Time Labels */}
        {data.timeLabels.map((label, i) => {
          const pos = getNodePos(i);
          return (
            <text
              key={`tl-${i}`}
              x={pos.x + nodeW / 2}
              y={pos.y + nodeH + 20}
              textAnchor="middle"
              fontSize="10"
              fill="rgba(128,128,128,0.5)"
              style={{ fontFamily: "var(--font-mono, monospace)" }}
            >
              {label}
            </text>
          );
        })}
      </svg>

      {/* 스킵된 단계 표시 */}
      {data.skipped.length > 0 && (
        <div className="flex items-center gap-2 mt-1 ml-8">
          <span className="text-[10px] text-[var(--color-text-muted)]">건너뛴 단계:</span>
          {data.skipped.map((s) => (
            <span key={s} className="text-[10px] px-2 py-0.5 rounded border border-dashed border-gray-300 text-gray-400">{s}</span>
          ))}
        </div>
      )}
    </div>
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
