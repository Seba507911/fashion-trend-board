import { SIGNAL_LABELS, ORIGIN_LABELS, ORIGIN_COLORS } from "./mockData";

/* ── Shared small components ── */

function ConfidenceBadge({ value }) {
  let cls;
  if (value >= 70) cls = "bg-emerald-50 text-emerald-700 border-emerald-200";
  else if (value >= 40) cls = "bg-amber-50 text-amber-700 border-amber-200";
  else cls = "bg-gray-50 text-gray-500 border-gray-200";
  return (
    <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full border ${cls}`}>
      {value}%
    </span>
  );
}

function SignalDot({ value }) {
  if (value >= 0.5) return <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)]" />;
  if (value > 0) return <span className="w-1.5 h-1.5 rounded-full bg-gray-300" />;
  return <span className="w-1.5 h-1.5 rounded-full border border-gray-200 bg-white" />;
}

/* ── Mini keyword card inside a matrix cell ── */

function MatrixKeywordCard({ kw, isSelected, onSelect }) {
  const originColor = ORIGIN_COLORS[kw.origin] || "#999";

  return (
    <button
      onClick={() => onSelect(isSelected ? null : kw.id)}
      className={`w-full text-left p-3 rounded-md border transition-all ${
        isSelected
          ? "border-[var(--color-primary)] bg-[var(--color-primary)]/5 shadow-sm"
          : "border-[var(--color-border)] bg-white hover:border-[var(--color-primary)]/30 hover:shadow-sm"
      }`}
    >
      {/* Row 1: keyword + confidence */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-[var(--color-text)] truncate mr-2">
          {kw.keyword}
        </span>
        <ConfidenceBadge value={kw.confidence} />
      </div>

      {/* Row 2: 5 signal dots */}
      <div className="flex items-center gap-2 mb-2">
        {SIGNAL_LABELS.map(({ key, label }) => (
          <div key={key} className="flex items-center gap-0.5">
            <SignalDot value={kw.signals[key]} />
            <span className="text-[9px] text-[var(--color-text-muted)]">{label}</span>
          </div>
        ))}
      </div>

      {/* Row 3: origin + pool tags */}
      <div className="flex items-center gap-1">
        <span
          className="text-[9px] px-1.5 py-0.5 rounded text-white"
          style={{ backgroundColor: originColor }}
        >
          {ORIGIN_LABELS[kw.origin]}
        </span>
        <span className={`text-[9px] px-1.5 py-0.5 rounded border ${
          kw.pool === "A"
            ? "border-blue-200 bg-blue-50 text-blue-600"
            : "border-orange-200 bg-orange-50 text-orange-600"
        }`}>
          풀 {kw.pool}
        </span>
      </div>
    </button>
  );
}

/* ── Quadrant cell ── */

const QUADRANT_STYLES = {
  spreading: { accent: "#059669", bg: "bg-emerald-50/40", icon: "↗" },
  marketSelf: { accent: "#D97706", bg: "bg-amber-50/40", icon: "→" },
  latent: { accent: "#3266ad", bg: "bg-blue-50/40", icon: "↑" },
  unknown: { accent: "#999", bg: "bg-gray-50/40", icon: "?" },
};

function MatrixCell({ title, subtitle, quadrant, keywords, selectedId, onSelect }) {
  const style = QUADRANT_STYLES[quadrant];

  return (
    <div className={`rounded-lg border border-[var(--color-border)] p-4 min-h-[200px] ${style.bg}`}>
      {/* Cell header */}
      <div className="flex items-center gap-2 mb-1">
        <span
          className="w-5 h-5 rounded flex items-center justify-center text-[11px] font-bold text-white"
          style={{ backgroundColor: style.accent }}
        >
          {style.icon}
        </span>
        <span className="text-sm font-semibold text-[var(--color-text)]">{title}</span>
        <span className="text-[10px] text-[var(--color-text-muted)] ml-auto">
          {keywords.length}개
        </span>
      </div>
      <p className="text-[10px] text-[var(--color-text-muted)] mb-3">{subtitle}</p>

      {/* Keyword cards */}
      <div className="flex flex-col gap-2">
        {keywords
          .sort((a, b) => b.confidence - a.confidence)
          .map((kw) => (
            <MatrixKeywordCard
              key={kw.id}
              kw={kw}
              isSelected={selectedId === kw.id}
              onSelect={onSelect}
            />
          ))}
        {keywords.length === 0 && (
          <div className="flex items-center justify-center h-[80px] text-[11px] text-[var(--color-text-muted)] italic">
            해당 키워드 없음
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Main MatrixView ── */

export default function MatrixView({ keywords, selectedId, onSelect }) {
  const cells = {
    spreading: [],  // runway strong + market strong
    marketSelf: [], // runway weak + market strong
    latent: [],     // runway strong + market weak
    unknown: [],    // runway weak + market weak
  };

  keywords.forEach((kw) => {
    const runwayStrong = kw.signals.runway >= 0.5;
    const marketStrong = kw.signals.market >= 0.5;
    if (runwayStrong && marketStrong) cells.spreading.push(kw);
    else if (!runwayStrong && marketStrong) cells.marketSelf.push(kw);
    else if (runwayStrong && !marketStrong) cells.latent.push(kw);
    else cells.unknown.push(kw);
  });

  return (
    <div>
      {/* X-axis header */}
      <div className="flex mb-2">
        <div className="w-[60px] shrink-0" />
        <div className="flex-1 grid grid-cols-2 gap-3">
          <div className="text-center text-[11px] font-semibold text-[var(--color-text-secondary)] tracking-wide">
            런웨이 강 <span className="text-[var(--color-text-muted)] font-normal">(≥0.5)</span>
          </div>
          <div className="text-center text-[11px] font-semibold text-[var(--color-text-secondary)] tracking-wide">
            런웨이 약 <span className="text-[var(--color-text-muted)] font-normal">(&lt;0.5)</span>
          </div>
        </div>
      </div>

      {/* Matrix body */}
      <div className="flex gap-0">
        {/* Y-axis labels */}
        <div className="w-[60px] shrink-0 grid grid-rows-2 gap-3">
          <div className="flex items-center justify-end pr-3">
            <span className="text-[11px] font-semibold text-[var(--color-text-secondary)] [writing-mode:vertical-lr] rotate-180 tracking-wide">
              마켓 강
            </span>
          </div>
          <div className="flex items-center justify-end pr-3">
            <span className="text-[11px] font-semibold text-[var(--color-text-secondary)] [writing-mode:vertical-lr] rotate-180 tracking-wide">
              마켓 약
            </span>
          </div>
        </div>

        {/* 2×2 grid */}
        <div className="flex-1 grid grid-cols-2 grid-rows-2 gap-3">
          <MatrixCell
            title="확산 중"
            subtitle="런웨이에서 시작, 마켓까지 도달한 검증된 트렌드"
            quadrant="spreading"
            keywords={cells.spreading}
            selectedId={selectedId}
            onSelect={onSelect}
          />
          <MatrixCell
            title="마켓 자생"
            subtitle="런웨이 시그널 없이 마켓에서 자체 성장"
            quadrant="marketSelf"
            keywords={cells.marketSelf}
            selectedId={selectedId}
            onSelect={onSelect}
          />
          <MatrixCell
            title="잠재 시그널"
            subtitle="런웨이에서 강하지만 아직 마켓에 미반영"
            quadrant="latent"
            keywords={cells.latent}
            selectedId={selectedId}
            onSelect={onSelect}
          />
          <MatrixCell
            title="미확인"
            subtitle="두 시그널 모두 약한 초기 단계"
            quadrant="unknown"
            keywords={cells.unknown}
            selectedId={selectedId}
            onSelect={onSelect}
          />
        </div>
      </div>
    </div>
  );
}
