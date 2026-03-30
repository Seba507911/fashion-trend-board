import { useState } from "react";

const RATINGS = [
  { value: "fit", label: "핏함", desc: "분석이 현업 눈높이에 적절하다", color: "border-emerald-400 bg-emerald-50 text-emerald-800" },
  { value: "uncertain", label: "애매", desc: "일부 맞지만 보완이 필요하다", color: "border-amber-400 bg-amber-50 text-amber-800" },
  { value: "off", label: "동떨어짐", desc: "현업과 괴리가 있다", color: "border-red-400 bg-red-50 text-red-800" },
];

export default function SectionReview({ sectionId, season = "26SS", savedReview, onSave }) {
  const [rating, setRating] = useState(savedReview?.rating || null);
  const [comment, setComment] = useState(savedReview?.comment || "");
  const [reviewer, setReviewer] = useState(savedReview?.reviewer || "");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    if (!rating) return;
    setSaving(true);
    try {
      await onSave({ sectionId, rating, comment, reviewer, season });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mt-8 pt-6 border-t-2 border-dashed border-[var(--color-border)]">
      <h4 className="text-sm font-bold text-[var(--color-text)] mb-3">
        이 섹션에 대한 리뷰
      </h4>

      <div className="flex gap-2 mb-4 flex-wrap">
        {RATINGS.map((r) => (
          <button
            key={r.value}
            onClick={() => { setRating(r.value); setSaved(false); }}
            className={`px-4 py-2 rounded-lg border-2 text-left transition-all ${
              rating === r.value ? r.color : "border-[var(--color-border)] bg-white hover:bg-gray-50"
            }`}
          >
            <div className="text-sm font-semibold">{r.label}</div>
            <div className="text-[11px] text-[var(--color-text-muted)] mt-0.5">{r.desc}</div>
          </button>
        ))}
      </div>

      <textarea
        value={comment}
        onChange={(e) => { setComment(e.target.value); setSaved(false); }}
        placeholder="의견이나 보완 사항을 자유롭게 적어주세요. 예) '이 부분은 실제 리테일과 다르다', '여기에 OO 키워드가 빠져 있다' 등"
        rows={3}
        className="w-full text-sm p-3 border border-[var(--color-border)] rounded-lg resize-none mb-3 focus:outline-none focus:border-[var(--color-primary)] placeholder:text-gray-400"
      />

      <div className="flex items-center gap-3">
        <input
          type="text"
          value={reviewer}
          onChange={(e) => { setReviewer(e.target.value); setSaved(false); }}
          placeholder="이름"
          className="text-sm px-3 py-2 border border-[var(--color-border)] rounded-lg w-36 focus:outline-none focus:border-[var(--color-primary)]"
        />
        <button
          onClick={handleSave}
          disabled={!rating || saving}
          className={`px-5 py-2 text-sm font-semibold rounded-lg transition-colors ${
            rating
              ? "bg-[var(--color-primary)] text-white hover:opacity-90"
              : "bg-gray-100 text-gray-400 cursor-not-allowed"
          }`}
        >
          {saving ? "저장 중..." : saved ? "저장 완료" : "리뷰 저장"}
        </button>
        {savedReview?.rating && !saved && (
          <span className="text-[11px] text-[var(--color-text-muted)]">
            이전 리뷰: {RATINGS.find(r => r.value === savedReview.rating)?.label}
            {savedReview.reviewer ? ` (${savedReview.reviewer})` : ""}
          </span>
        )}
      </div>
    </div>
  );
}
