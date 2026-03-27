const CATEGORY_COLORS = {
  color: "bg-rose-50 text-rose-700 border-rose-200",
  material: "bg-emerald-50 text-emerald-700 border-emerald-200",
  silhouette: "bg-violet-50 text-violet-700 border-violet-200",
  item: "bg-sky-50 text-sky-700 border-sky-200",
  style: "bg-amber-50 text-amber-700 border-amber-200",
};

const TIER_LABELS = { 1: "Tier 1", 2: "Tier 2", 3: "Tier 3", 4: "Tier 4" };

const REVIEW_BADGE = {
  essential: { label: "핵심", cls: "bg-blue-50 text-blue-700 border-blue-200" },
  reference: { label: "참고", cls: "bg-gray-50 text-gray-600 border-gray-200" },
  exclude: { label: "제외", cls: "bg-red-50 text-red-600 border-red-200" },
};

export default function ExpertKeywordCard({ data, isSelected, onClick }) {
  const catCls = CATEGORY_COLORS[data.category] || "bg-gray-50 text-gray-600 border-gray-200";
  const review = data.review_status ? REVIEW_BADGE[data.review_status] : null;

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-4 rounded-lg border transition-all ${
        isSelected
          ? "border-[var(--color-primary)] bg-[var(--color-primary)]/5 shadow-sm"
          : "border-[var(--color-border)] bg-white hover:border-[var(--color-primary)]/30 hover:shadow-sm"
      }`}
    >
      {/* Top: keyword name + source count */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div>
          <div className="text-sm font-semibold text-[var(--color-text)]">{data.keyword_kr}</div>
          <div className="text-[11px] text-[var(--color-text-muted)]">{data.keyword.replace(/_/g, " ")}</div>
        </div>
        <div className="text-[11px] font-semibold text-[var(--color-primary)] bg-[var(--color-primary)]/8 px-2 py-0.5 rounded-full shrink-0">
          {data.source_count}개 소스
        </div>
      </div>

      {/* Tags row */}
      <div className="flex items-center gap-1.5 flex-wrap mb-2">
        <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded border ${catCls}`}>
          {data.category}
        </span>
        <span className="text-[10px] font-medium px-1.5 py-0.5 rounded border border-[var(--color-border)] text-[var(--color-text-muted)]">
          {TIER_LABELS[data.tier] || `Tier ${data.tier}`}
        </span>
        {data.pool && (
          <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded border ${
            data.pool === "A"
              ? "bg-indigo-50 text-indigo-700 border-indigo-200"
              : "bg-orange-50 text-orange-700 border-orange-200"
          }`}>
            풀 {data.pool}
          </span>
        )}
        {review && (
          <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded border ${review.cls}`}>
            {review.label}
          </span>
        )}
      </div>

      {/* Description snippet */}
      <p className="text-[11px] text-[var(--color-text-secondary)] leading-relaxed line-clamp-2">
        {data.description}
      </p>
    </button>
  );
}
