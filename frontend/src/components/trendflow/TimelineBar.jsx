export default function TimelineBar({ season, strength, label }) {
  return (
    <div className="flex items-center gap-3 mb-1.5">
      <span className="w-[48px] text-xs text-[var(--color-text-secondary)] font-medium shrink-0">
        {season}
      </span>
      <div className="flex-1 h-6 bg-gray-50 rounded overflow-hidden relative">
        <div
          className="h-full rounded flex items-center px-2 text-[10px] font-medium text-white whitespace-nowrap transition-all duration-500"
          style={{
            width: `${strength}%`,
            backgroundColor: "var(--color-primary)",
            opacity: 0.3 + (strength / 100) * 0.7,
          }}
        >
          {label}
        </div>
      </div>
    </div>
  );
}
