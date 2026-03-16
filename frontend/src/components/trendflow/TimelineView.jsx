import { SEASONS, ORIGIN_COLORS } from "./mockData";

function getHeatColor(strength) {
  if (strength >= 70) return { bg: "var(--color-primary)", opacity: 0.9 };
  if (strength >= 50) return { bg: "var(--color-primary)", opacity: 0.6 };
  if (strength >= 30) return { bg: "var(--color-primary)", opacity: 0.35 };
  if (strength > 0) return { bg: "var(--color-primary)", opacity: 0.15 };
  return { bg: "transparent", opacity: 0 };
}

export default function TimelineView({ keywords, selectedId, onSelect }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="text-left text-[11px] font-medium text-[var(--color-text-muted)] pb-2 pr-4 w-[160px]">
              키워드
            </th>
            {SEASONS.map((s) => (
              <th
                key={s}
                className="text-center text-[11px] font-medium text-[var(--color-text-muted)] pb-2 w-[80px]"
              >
                {s}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {keywords.map((kw) => {
            const seasonMap = {};
            (kw.timeline || []).forEach((t) => {
              seasonMap[t.season] = t;
            });

            return (
              <tr
                key={kw.id}
                onClick={() => onSelect(selectedId === kw.id ? null : kw.id)}
                className={`cursor-pointer transition-colors ${
                  selectedId === kw.id
                    ? "bg-[var(--color-primary)]/5"
                    : "hover:bg-gray-50"
                }`}
              >
                <td className="py-1.5 pr-4">
                  <div className="flex items-center gap-2">
                    <span
                      className="w-2 h-2 rounded-full shrink-0"
                      style={{ backgroundColor: ORIGIN_COLORS[kw.origin] || "#999" }}
                    />
                    <span className="text-xs font-medium text-[var(--color-text)]">
                      {kw.keyword}
                    </span>
                    <span className="text-[10px] text-[var(--color-text-muted)]">
                      {kw.confidence}%
                    </span>
                  </div>
                </td>
                {SEASONS.map((s) => {
                  const entry = seasonMap[s];
                  const { bg, opacity } = entry
                    ? getHeatColor(entry.strength)
                    : { bg: "transparent", opacity: 0 };
                  return (
                    <td key={s} className="py-1.5 px-1">
                      <div
                        className="h-7 rounded flex items-center justify-center text-[9px] font-medium transition-all"
                        style={{
                          backgroundColor: bg,
                          opacity: opacity || undefined,
                          color: opacity >= 0.5 ? "white" : "var(--color-text-muted)",
                        }}
                        title={entry?.label}
                      >
                        {entry ? entry.strength : ""}
                      </div>
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
