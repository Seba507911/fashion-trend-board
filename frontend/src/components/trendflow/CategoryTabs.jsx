import { CATEGORIES } from "./mockData";

const VIEW_OPTIONS = [
  { key: "card", label: "카드 뷰" },
  { key: "matrix", label: "매트릭스 뷰" },
  { key: "timeline", label: "타임라인 뷰" },
];

export default function CategoryTabs({ category, setCategory, view, setView }) {
  return (
    <div className="flex items-center justify-between">
      {/* Category tabs */}
      <div className="flex gap-0">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`px-4 py-2 text-[13px] font-medium border-b-2 transition-all bg-transparent ${
              category === cat
                ? "text-[var(--color-primary)] border-[var(--color-primary)]"
                : "text-[var(--color-text-secondary)] border-transparent hover:text-[var(--color-text)]"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* View toggle */}
      <div className="flex bg-[#F5F5F5] rounded-md p-0.5">
        {VIEW_OPTIONS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setView(key)}
            className={`px-3 py-1 text-[11px] rounded transition-all ${
              view === key
                ? "bg-white text-[var(--color-text)] font-medium shadow-sm"
                : "text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
