import { useNavigate } from "react-router-dom";
import { SIGNAL_LABELS, ORIGIN_LABELS } from "./mockData";
import SignalBar from "./SignalBar";
import TimelineBar from "./TimelineBar";

const CATEGORY_LABELS = {
  color: "컬러",
  material: "소재",
  silhouette: "실루엣",
  item: "아이템",
  style: "스타일",
};

export default function KeywordDetailPanel({ data, season, onClose }) {
  const navigate = useNavigate();

  if (!data) return null;

  return (
    <div className="border border-[var(--color-primary)]/20 bg-[var(--color-primary)]/[0.02] rounded-lg p-6 mt-3 mb-3">
      {/* Header */}
      <div className="flex items-start justify-between mb-5">
        <div>
          <h3 className="text-lg font-semibold text-[var(--color-text)]">
            {data.keyword}
          </h3>
          <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
            {CATEGORY_LABELS[data.category]} · {ORIGIN_LABELS[data.origin]} · 풀 {data.pool} · Confidence {data.confidence}%
          </p>
        </div>
        <button
          onClick={onClose}
          className="p-1 text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M6 6l8 8M14 6l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Signal Strength */}
        <div>
          <h4 className="text-xs font-semibold text-[var(--color-text)] mb-3 uppercase tracking-wide">
            시그널 강도
          </h4>
          {SIGNAL_LABELS.map(({ key, label }) => (
            <SignalBar
              key={key}
              label={label}
              value={data.signals[key]}
              detail={data.signalDetails[key]}
            />
          ))}
        </div>

        {/* Season Timeline */}
        <div>
          <h4 className="text-xs font-semibold text-[var(--color-text)] mb-3 uppercase tracking-wide">
            시즌별 전파 타임라인
          </h4>
          {data.timeline.map((t) => (
            <TimelineBar
              key={t.season}
              season={t.season}
              strength={t.strength}
              label={t.label}
            />
          ))}
        </div>

        {/* Market Brand Distribution */}
        <div>
          <h4 className="text-xs font-semibold text-[var(--color-text)] mb-3 uppercase tracking-wide">
            마켓 브랜드 분포
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.brands.map((b) => (
              <button
                key={b.brand}
                onClick={() => navigate(`/?keyword=${encodeURIComponent(data.keyword)}`)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-[var(--color-border)] bg-white text-xs text-[var(--color-text-secondary)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition-all"
              >
                {b.brand}
                <span className="text-[10px] bg-gray-100 px-1.5 py-0.5 rounded-full font-medium">
                  {b.count}
                </span>
              </button>
            ))}
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-[var(--color-border)]">
            <button
              onClick={() => navigate(`/runway?tag=${encodeURIComponent(data.keyword)}&season=${encodeURIComponent(season)}`)}
              className="text-[11px] px-3 py-1.5 rounded border border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition-all"
            >
              런웨이 룩 보기
            </button>
            <button
              onClick={() => navigate(`/?keyword=${encodeURIComponent(data.keyword)}`)}
              className="text-[11px] px-3 py-1.5 rounded border border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition-all"
            >
              마켓 상품 보기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
