import {
  COLOR_KEYWORDS, MATERIAL_KEYWORDS, SILHOUETTE_KEYWORDS,
  ITEM_KEYWORDS, STYLE_MACRO, STYLE_NICHE,
  YOY_GROWTH, COLLECTION_SHARE,
  POOL_A, POOL_B,
} from "../components/expert/reportData";

/* ── Helper: count keywords per category ── */
function countTiers(kw) {
  return Object.values(kw).reduce((sum, tier) => sum + tier.items.length, 0);
}

const CATEGORIES = [
  { label: "컬러", count: countTiers(COLOR_KEYWORDS), color: "#3266ad", data: COLOR_KEYWORDS },
  { label: "소재", count: countTiers(MATERIAL_KEYWORDS), color: "#D97706", data: MATERIAL_KEYWORDS },
  { label: "실루엣", count: countTiers(SILHOUETTE_KEYWORDS), color: "#059669", data: SILHOUETTE_KEYWORDS },
  { label: "아이템", count: countTiers(ITEM_KEYWORDS), color: "#8B5CF6", data: ITEM_KEYWORDS },
  { label: "스타일", count: STYLE_MACRO.length + STYLE_NICHE.length, color: "#DC2626", data: null },
];

const TOTAL = CATEGORIES.reduce((s, c) => s + c.count, 0);

function TierBadge({ tier }) {
  const colors = {
    "Tier 1": "bg-red-100 text-red-700",
    "Tier 2": "bg-orange-100 text-orange-700",
    "Tier 3": "bg-yellow-100 text-yellow-700",
    "Tier 4": "bg-gray-100 text-gray-500",
  };
  return <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded ${colors[tier] || "bg-gray-100 text-gray-500"}`}>{tier}</span>;
}

function PoolBadge({ pool }) {
  const cls = pool === "A" ? "bg-indigo-100 text-indigo-700" : "bg-orange-100 text-orange-700";
  return <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded ${cls}`}>Pool {pool}</span>;
}

export default function ExpertReview() {
  return (
    <main className="flex-1 overflow-y-auto bg-[var(--color-bg)]">
      <div className="max-w-[960px] mx-auto px-8 py-10">

        {/* Header */}
        <div className="mb-8">
          <h1 className="font-['Lora'] text-xl font-semibold tracking-wide">Expert Review</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            WGSN 26SS 리포트 기반 키워드 분석 요약 · 참고용
          </p>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-5 gap-3 mb-8">
          {CATEGORIES.map((c) => (
            <div key={c.label} className="bg-white border border-[var(--color-border)] rounded-lg p-4 text-center">
              <div className="text-2xl font-bold font-['Lora']" style={{ color: c.color }}>{c.count}</div>
              <div className="text-xs font-medium text-[var(--color-text-secondary)] mt-1">{c.label}</div>
            </div>
          ))}
        </div>

        {/* Distribution Bar */}
        <div className="bg-white border border-[var(--color-border)] rounded-lg p-5 mb-8">
          <h3 className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-3">
            카테고리 분포 ({TOTAL} keywords)
          </h3>
          <div className="flex h-8 rounded-lg overflow-hidden mb-3">
            {CATEGORIES.map((c) => (
              <div
                key={c.label}
                style={{ width: `${(c.count / TOTAL * 100)}%`, backgroundColor: c.color }}
                className="flex items-center justify-center text-white text-[10px] font-bold"
                title={`${c.label}: ${c.count}`}
              >
                {c.count > 5 && c.label}
              </div>
            ))}
          </div>
          <div className="flex gap-4 flex-wrap">
            {CATEGORIES.map((c) => (
              <div key={c.label} className="flex items-center gap-1.5 text-[11px]">
                <span className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: c.color }} />
                <span className="text-[var(--color-text-secondary)]">{c.label}</span>
                <span className="font-semibold">{c.count}</span>
                <span className="text-[var(--color-text-muted)]">({Math.round(c.count / TOTAL * 100)}%)</span>
              </div>
            ))}
          </div>
        </div>

        {/* Pool A/B Summary */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="bg-white border border-indigo-200 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-3">
              <PoolBadge pool="A" />
              <span className="text-sm font-semibold text-[var(--color-text)]">
                런웨이 확인 ({POOL_A.items?.length || 49})
              </span>
            </div>
            <p className="text-xs text-[var(--color-text-secondary)] mb-3">전문가 예측 + 런웨이 출현 모두 확인된 키워드</p>
            <div className="flex flex-wrap gap-1.5">
              {(POOL_A.items || []).slice(0, 20).map((kw, i) => (
                <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                  {kw.keyword || kw}
                </span>
              ))}
              {(POOL_A.items?.length || 0) > 20 && (
                <span className="text-[10px] text-[var(--color-text-muted)]">+{POOL_A.items.length - 20} more</span>
              )}
            </div>
          </div>
          <div className="bg-white border border-orange-200 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-3">
              <PoolBadge pool="B" />
              <span className="text-sm font-semibold text-[var(--color-text)]">
                전문가 독립 예측 ({POOL_B.items?.length || 12})
              </span>
            </div>
            <p className="text-xs text-[var(--color-text-secondary)] mb-3">전문가만 예측, 런웨이 미출현 — 독립적 시그널</p>
            <div className="flex flex-wrap gap-1.5">
              {(POOL_B.items || []).map((kw, i) => (
                <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-orange-50 text-orange-700 border border-orange-200">
                  {kw.keyword || kw}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* YoY Growth + Collection Share */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="bg-white border border-[var(--color-border)] rounded-lg p-5">
            <h3 className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-3">YoY 성장률 TOP</h3>
            <div className="space-y-2">
              {YOY_GROWTH.slice(0, 8).map((item, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-xs text-[var(--color-text)]">{item.keyword || item.label || item}</span>
                  <span className="text-xs font-bold text-emerald-600">{item.growth || item.value || ""}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-white border border-[var(--color-border)] rounded-lg p-5">
            <h3 className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-3">컬렉션 채택률</h3>
            <div className="space-y-2">
              {COLLECTION_SHARE.slice(0, 8).map((item, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="text-xs text-[var(--color-text)] flex-1">{item.keyword || item.label || item}</span>
                  <div className="w-24 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-[var(--color-primary)] rounded-full" style={{ width: `${item.pct || item.value || 50}%` }} />
                  </div>
                  <span className="text-[10px] text-[var(--color-text-muted)] w-10 text-right">{item.pct || item.value || ""}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Category Keyword Lists (compact) */}
        {CATEGORIES.filter(c => c.data).map((cat) => (
          <div key={cat.label} className="bg-white border border-[var(--color-border)] rounded-lg p-5 mb-4">
            <h3 className="text-sm font-semibold mb-3" style={{ color: cat.color }}>
              {cat.label} 키워드 ({cat.count})
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(cat.data).map(([tierKey, tier]) =>
                tier.items.map((kw, i) => (
                  <span
                    key={`${tierKey}-${i}`}
                    className="text-[10px] px-2 py-1 rounded border border-[var(--color-border)] text-[var(--color-text-secondary)] flex items-center gap-1"
                  >
                    <TierBadge tier={tier.label} />
                    {kw.keyword || kw}
                  </span>
                ))
              )}
            </div>
          </div>
        ))}

        <div className="text-center text-[11px] text-[var(--color-text-muted)] mt-6 py-4 border-t border-[var(--color-border)]">
          Source: WGSN 26SS Reports (77건) · NotebookLM 분석 · 참고용 데이터
        </div>
      </div>
    </main>
  );
}
