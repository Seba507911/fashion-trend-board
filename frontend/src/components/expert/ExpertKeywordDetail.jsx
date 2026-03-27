import { useState } from "react";
import { useNavigate } from "react-router-dom";

const REVIEW_OPTIONS = [
  { value: "essential", label: "핵심", desc: "F&F 브랜드에 직접 해당", cls: "border-blue-400 bg-blue-50" },
  { value: "reference", label: "참고", desc: "알아두면 좋음", cls: "border-gray-400 bg-gray-50" },
  { value: "exclude", label: "제외", desc: "우리와 무관", cls: "border-red-400 bg-red-50" },
];

const CATEGORY_LABEL = { color: "컬러", material: "소재", silhouette: "실루엣", item: "아이템", style: "스타일" };

export default function ExpertKeywordDetail({ data, onReview, onClose }) {
  const navigate = useNavigate();
  const [evaluation, setEvaluation] = useState(data.review_status || null);
  const [comment, setComment] = useState(data.review_comment || "");
  const [reviewer, setReviewer] = useState(data.reviewer || "");
  const [saving, setSaving] = useState(false);

  if (!data) return null;

  const handleSave = async () => {
    if (!evaluation) return;
    setSaving(true);
    try {
      await onReview({ keyword: data.keyword, evaluation, comment, reviewer, season: data.season });
    } finally {
      setSaving(false);
    }
  };

  const runwayKw = data.runway_keyword || data.keyword.replace(/_/g, " ");

  return (
    <div className="border border-[var(--color-primary)]/20 bg-[var(--color-primary)]/[0.02] rounded-lg p-6 mt-3 mb-3">
      {/* Header */}
      <div className="flex items-start justify-between mb-5">
        <div>
          <h2 className="text-lg font-bold text-[var(--color-text)]">{data.keyword_kr}</h2>
          <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
            {CATEGORY_LABEL[data.category] || data.category} · Tier {data.tier}
            {data.pool ? ` · 풀 ${data.pool}` : ""} · {data.source_count}개 소스
            {data.source ? ` · ${data.source.toUpperCase()}` : ""}
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-[var(--color-text-muted)] hover:text-[var(--color-text)] text-lg leading-none"
        >
          &times;
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left: WGSN Analysis */}
        <div className="md:col-span-2 flex flex-col gap-4">
          {/* Description */}
          <div>
            <h4 className="text-[11px] font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-1.5">
              WGSN 분석 요약
            </h4>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
              {data.description}
            </p>
          </div>

          {/* Themes */}
          {data.themes && data.themes.length > 0 && (
            <div>
              <h4 className="text-[11px] font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-1.5">
                매크로 테마 연결
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {data.themes.map((t) => (
                  <span
                    key={t}
                    className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-[var(--color-primary)]/8 text-[var(--color-primary)] border border-[var(--color-primary)]/15"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* F&F Relevance */}
          {data.f_and_f_relevance && (
            <div>
              <h4 className="text-[11px] font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-1.5">
                F&F 관련성
              </h4>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                data.f_and_f_relevance === "high"
                  ? "bg-emerald-50 text-emerald-700"
                  : "bg-amber-50 text-amber-700"
              }`}>
                {data.f_and_f_relevance === "high" ? "높음" : "중간"}
              </span>
            </div>
          )}

          {/* Related data (future) */}
          <div>
            <h4 className="text-[11px] font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-1.5">
              관련 데이터 (향후 연동)
            </h4>
            <div className="text-xs text-[var(--color-text-muted)] space-y-1">
              <div className="flex items-center gap-2">
                <span className="w-24">런웨이 VLM 매칭</span>
                <span className="text-[var(--color-text-secondary)]">— 연동 예정</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-24">마켓 상품 매칭</span>
                <span className="text-[var(--color-text-secondary)]">— 연동 예정</span>
              </div>
            </div>
          </div>

          {/* Navigation buttons */}
          <div className="flex gap-2 mt-1">
            <button
              onClick={() => navigate(`/runway?tag=${encodeURIComponent(runwayKw)}&season=${data.season}`)}
              className="px-3 py-1.5 text-xs font-medium rounded border border-[var(--color-primary)] text-[var(--color-primary)] hover:bg-[var(--color-primary)]/5"
            >
              런웨이에서 확인
            </button>
            <button
              onClick={() => navigate(`/market?keyword=${encodeURIComponent(runwayKw)}`)}
              className="px-3 py-1.5 text-xs font-medium rounded border border-[var(--color-primary)] text-[var(--color-primary)] hover:bg-[var(--color-primary)]/5"
            >
              마켓에서 확인
            </button>
          </div>
        </div>

        {/* Right: Review panel */}
        <div className="border-l border-[var(--color-border)] pl-5">
          <h4 className="text-[11px] font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-3">
            팀 리뷰
          </h4>

          <div className="flex flex-col gap-2 mb-3">
            {REVIEW_OPTIONS.map((opt) => (
              <label
                key={opt.value}
                className={`flex items-start gap-2 p-2 rounded border cursor-pointer transition-colors ${
                  evaluation === opt.value ? opt.cls : "border-[var(--color-border)] hover:bg-black/2"
                }`}
              >
                <input
                  type="radio"
                  name="review"
                  value={opt.value}
                  checked={evaluation === opt.value}
                  onChange={() => setEvaluation(opt.value)}
                  className="mt-0.5 accent-[var(--color-primary)]"
                />
                <div>
                  <div className="text-xs font-semibold">{opt.label}</div>
                  <div className="text-[10px] text-[var(--color-text-muted)]">{opt.desc}</div>
                </div>
              </label>
            ))}
          </div>

          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="코멘트 (선택)"
            rows={2}
            className="w-full text-xs p-2 border border-[var(--color-border)] rounded resize-none mb-2 focus:outline-none focus:border-[var(--color-primary)]"
          />

          <input
            type="text"
            value={reviewer}
            onChange={(e) => setReviewer(e.target.value)}
            placeholder="평가자 이름"
            className="w-full text-xs p-2 border border-[var(--color-border)] rounded mb-3 focus:outline-none focus:border-[var(--color-primary)]"
          />

          <button
            onClick={handleSave}
            disabled={!evaluation || saving}
            className={`w-full py-2 text-xs font-semibold rounded transition-colors ${
              evaluation
                ? "bg-[var(--color-primary)] text-white hover:opacity-90"
                : "bg-gray-100 text-gray-400 cursor-not-allowed"
            }`}
          >
            {saving ? "저장 중..." : "평가 저장"}
          </button>
        </div>
      </div>
    </div>
  );
}
