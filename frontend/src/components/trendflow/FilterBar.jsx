import { SEASONS, ZONINGS } from "./mockData";

export default function FilterBar({ season, setSeason, zoning, setZoning }) {
  return (
    <div className="flex flex-wrap items-center gap-6">
      {/* Season pills */}
      <div className="flex items-center gap-1.5">
        <span className="text-xs text-[var(--color-text-muted)] mr-1 font-medium">시즌</span>
        {SEASONS.map((s) => (
          <button
            key={s}
            onClick={() => setSeason(s)}
            className={`px-3 py-1 text-xs rounded-full border transition-all ${
              season === s
                ? "border-[var(--color-primary)] bg-[var(--color-primary)] text-white font-medium"
                : "border-[var(--color-border)] bg-white text-[var(--color-text-secondary)] hover:border-[var(--color-primary)]/40"
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Zoning pills */}
      <div className="flex items-center gap-1.5">
        <span className="text-xs text-[var(--color-text-muted)] mr-1 font-medium">조닝</span>
        {ZONINGS.map((z) => (
          <button
            key={z}
            onClick={() => setZoning(z)}
            className={`px-3 py-1 text-xs rounded-full border transition-all ${
              zoning === z
                ? "border-[var(--color-primary)] bg-[var(--color-primary)] text-white font-medium"
                : "border-[var(--color-border)] bg-white text-[var(--color-text-secondary)] hover:border-[var(--color-primary)]/40"
            }`}
          >
            {z}
          </button>
        ))}
      </div>
    </div>
  );
}
