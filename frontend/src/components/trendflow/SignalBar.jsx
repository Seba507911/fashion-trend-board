export default function SignalBar({ label, value, detail }) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex items-center gap-3 mb-2">
      <span className="w-[60px] text-xs text-[var(--color-text-secondary)] font-medium shrink-0">
        {label}
      </span>
      <div className="flex-1 h-5 bg-gray-100 rounded-full overflow-hidden relative">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${pct}%`,
            backgroundColor: pct >= 50 ? "var(--color-primary)" : "#94a3b8",
          }}
        />
      </div>
      <span className="text-[11px] text-[var(--color-text-muted)] w-[120px] shrink-0 text-right">
        {detail}
      </span>
    </div>
  );
}
