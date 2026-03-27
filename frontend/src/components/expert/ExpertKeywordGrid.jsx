import ExpertKeywordCard from "./ExpertKeywordCard";

const TIER_NAMES = {
  1: "Tier 1 — 핵심 합의",
  2: "Tier 2 — 주요",
  3: "Tier 3 — 서브",
  4: "Tier 4 — 니치",
};

export default function ExpertKeywordGrid({ keywords, selectedId, onSelect }) {
  if (!keywords || keywords.length === 0) {
    return (
      <div className="text-center py-12 text-[var(--color-text-muted)] text-sm">
        해당 조건의 키워드가 없습니다.
      </div>
    );
  }

  // Group by tier
  const byTier = {};
  keywords.forEach((kw) => {
    const t = kw.tier || 9;
    if (!byTier[t]) byTier[t] = [];
    byTier[t].push(kw);
  });

  return (
    <div className="flex flex-col gap-6">
      {Object.entries(byTier)
        .sort(([a], [b]) => Number(a) - Number(b))
        .map(([tier, items]) => (
          <div key={tier}>
            <div className="flex items-center gap-2 mb-3">
              <h3 className="text-xs font-bold text-[var(--color-text-muted)] tracking-wide uppercase">
                {TIER_NAMES[tier] || `Tier ${tier}`}
              </h3>
              <span className="text-[10px] text-[var(--color-text-muted)]">({items.length})</span>
            </div>
            <div
              className="grid gap-3"
              style={{ gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))" }}
            >
              {items.map((kw) => (
                <ExpertKeywordCard
                  key={kw.keyword}
                  data={kw}
                  isSelected={selectedId === kw.keyword}
                  onClick={() => onSelect(selectedId === kw.keyword ? null : kw.keyword)}
                />
              ))}
            </div>
          </div>
        ))}
    </div>
  );
}
