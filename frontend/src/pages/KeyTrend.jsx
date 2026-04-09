export default function KeyTrend() {
  return (
    <main className="flex-1 overflow-hidden bg-[var(--color-bg)] flex flex-col">
      {/* Test Banner */}
      <div className="shrink-0 bg-amber-50 border-b border-amber-200 px-8 py-2.5 flex items-center gap-2">
        <span className="text-amber-600 text-sm font-bold">TEST</span>
        <span className="text-amber-700 text-xs">
          팀 동료 분석 기반 목업 — 26 S/S 런웨이 인텔리전스 (33 Brands · ~1,800 Looks · 27 Show Notes)
        </span>
      </div>

      {/* Embedded HTML */}
      <iframe
        src="/docs/ej_trend_runway_test.html"
        className="flex-1 w-full border-none"
        title="Key Trend — 26 S/S Runway Intelligence"
      />
    </main>
  );
}
