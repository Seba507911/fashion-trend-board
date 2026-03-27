const SEASONS = ["24SS", "24FW", "25SS", "25FW", "26SS", "26FW"];
const CATEGORIES = [
  { label: "전체", value: null },
  { label: "컬러", value: "color" },
  { label: "소재", value: "material" },
  { label: "실루엣", value: "silhouette" },
  { label: "아이템", value: "item" },
  { label: "스타일", value: "style" },
];
const POOLS = [
  { label: "전체", value: null },
  { label: "풀 A", value: "A" },
  { label: "풀 B", value: "B" },
];

export default function ExpertFilterBar({ season, onSeasonChange, category, onCategoryChange, pool, onPoolChange }) {
  const pill = (active) =>
    `px-3 py-1 rounded-full border text-xs font-medium cursor-pointer transition-colors ${
      active
        ? "border-[var(--color-primary)] bg-[var(--color-primary)]/10 text-[var(--color-primary)]"
        : "border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-[var(--color-primary)]/40"
    }`;

  return (
    <div className="flex flex-col gap-3 sticky top-0 z-10 bg-[var(--color-bg)] pb-3 border-b border-[var(--color-border)]">
      {/* Season */}
      <div className="flex items-center gap-2">
        <span className="text-[11px] font-semibold text-[var(--color-text-muted)] w-12 shrink-0">시즌</span>
        <div className="flex gap-1.5 flex-wrap">
          {SEASONS.map((s) => (
            <button key={s} className={pill(season === s)} onClick={() => onSeasonChange(s)}>
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Category + Pool */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold text-[var(--color-text-muted)] w-12 shrink-0">카테고리</span>
          <div className="flex gap-1.5 flex-wrap">
            {CATEGORIES.map((c) => (
              <button key={c.label} className={pill(category === c.value)} onClick={() => onCategoryChange(c.value)}>
                {c.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold text-[var(--color-text-muted)] w-8 shrink-0">풀</span>
          <div className="flex gap-1.5">
            {POOLS.map((p) => (
              <button key={p.label} className={pill(pool === p.value)} onClick={() => onPoolChange(p.value)}>
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
