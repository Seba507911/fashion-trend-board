import { SIGNAL_LABELS, ORIGIN_LABELS, ORIGIN_COLORS } from "./mockData";

function ConfidenceBadge({ value }) {
  let bg, text;
  if (value >= 70) {
    bg = "bg-emerald-50 text-emerald-700 border-emerald-200";
  } else if (value >= 40) {
    bg = "bg-amber-50 text-amber-700 border-amber-200";
  } else {
    bg = "bg-gray-50 text-gray-500 border-gray-200";
  }
  return (
    <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${bg}`}>
      {value}%
    </span>
  );
}

function SignalDot({ status }) {
  if (status === "on") {
    return <span className="w-2 h-2 rounded-full bg-[var(--color-primary)]" />;
  }
  if (status === "weak") {
    return <span className="w-2 h-2 rounded-full bg-gray-300" />;
  }
  return <span className="w-2 h-2 rounded-full border border-gray-200 bg-white" />;
}

function getSignalStatus(value) {
  if (value >= 0.5) return "on";
  if (value > 0) return "weak";
  return "off";
}

const CATEGORY_LABELS = {
  color: "컬러",
  material: "소재",
  silhouette: "실루엣",
  item: "아이템",
  style: "스타일",
};

export default function KeywordCard({ data, isSelected, onClick }) {
  const originColor = ORIGIN_COLORS[data.origin] || "#999";

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-4 rounded-lg border transition-all ${
        isSelected
          ? "border-[var(--color-primary)] bg-[var(--color-primary)]/5 shadow-sm"
          : "border-[var(--color-border)] bg-white hover:border-[var(--color-primary)]/30 hover:shadow-sm"
      }`}
    >
      {/* Top: keyword + confidence */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-[var(--color-text)]">
          {data.keyword}
        </span>
        <ConfidenceBadge value={data.confidence} />
      </div>

      {/* Signal dots */}
      <div className="flex items-center gap-3 mb-3">
        {SIGNAL_LABELS.map(({ key, label }) => (
          <div key={key} className="flex items-center gap-1">
            <SignalDot status={getSignalStatus(data.signals[key])} />
            <span className="text-[10px] text-[var(--color-text-muted)]">{label}</span>
          </div>
        ))}
      </div>

      {/* Tags */}
      <div className="flex items-center gap-1.5 flex-wrap">
        <span className="text-[10px] px-2 py-0.5 rounded bg-gray-100 text-[var(--color-text-secondary)]">
          {CATEGORY_LABELS[data.category] || data.category}
        </span>
        <span
          className="text-[10px] px-2 py-0.5 rounded text-white"
          style={{ backgroundColor: originColor }}
        >
          {ORIGIN_LABELS[data.origin]}
        </span>
        <span className={`text-[10px] px-2 py-0.5 rounded border ${
          data.pool === "A"
            ? "border-blue-200 bg-blue-50 text-blue-600"
            : "border-orange-200 bg-orange-50 text-orange-600"
        }`}>
          풀 {data.pool}
        </span>
      </div>
    </button>
  );
}
