import { useState, useMemo } from "react";
import ExpertFilterBar from "../components/expert/ExpertFilterBar";
import ExpertKeywordGrid from "../components/expert/ExpertKeywordGrid";
import ExpertKeywordDetail from "../components/expert/ExpertKeywordDetail";
import { useExpertKeywords, useExpertKeywordDetail, useExpertReview } from "../hooks/useExpertKeywords";

export default function ExpertReview() {
  const [season, setSeason] = useState("26SS");
  const [category, setCategory] = useState(null);
  const [pool, setPool] = useState(null);
  const [selectedId, setSelectedId] = useState(null);

  const { data, isLoading } = useExpertKeywords({ season, category, pool });
  const keywords = data?.keywords || [];
  const total = data?.total || 0;
  const byTier = data?.by_tier || {};

  const selectedKeyword = useMemo(
    () => keywords.find((kw) => kw.keyword === selectedId),
    [keywords, selectedId]
  );

  const { data: detailData } = useExpertKeywordDetail({
    keyword: selectedId,
    season,
  });

  const reviewMutation = useExpertReview();

  const panelData = useMemo(() => {
    if (!selectedKeyword) return null;
    return { ...selectedKeyword, ...(detailData || {}) };
  }, [selectedKeyword, detailData]);

  const handleSeasonChange = (s) => {
    setSeason(s);
    setSelectedId(null);
  };
  const handleCategoryChange = (c) => {
    setCategory(c);
    setSelectedId(null);
  };
  const handlePoolChange = (p) => {
    setPool(p);
    setSelectedId(null);
  };

  const handleReview = async (reviewData) => {
    await reviewMutation.mutateAsync(reviewData);
  };

  // Summary stats
  const poolACnt = keywords.filter((k) => k.pool === "A").length;
  const poolBCnt = keywords.filter((k) => k.pool === "B").length;
  const reviewedCnt = keywords.filter((k) => k.review_status).length;

  return (
    <div className="flex flex-col gap-4 h-full overflow-y-auto px-6 py-5">
      {/* Page header */}
      <div>
        <h1 className="text-xl font-bold text-[var(--color-text)]">Expert Report Review</h1>
        <p className="text-xs text-[var(--color-text-muted)] mt-1">
          WGSN 77건 리포트 기반 키워드 분석 — 팀 리뷰 및 풀 A/B 검증
        </p>
      </div>

      {/* Filter bar */}
      <ExpertFilterBar
        season={season}
        onSeasonChange={handleSeasonChange}
        category={category}
        onCategoryChange={handleCategoryChange}
        pool={pool}
        onPoolChange={handlePoolChange}
      />

      {/* Summary bar */}
      <div className="flex items-center gap-4 text-[11px] text-[var(--color-text-muted)]">
        <span>
          전체 <strong className="text-[var(--color-text)]">{total}</strong>개 키워드
        </span>
        {Object.entries(byTier)
          .sort(([a], [b]) => Number(a) - Number(b))
          .map(([t, cnt]) => (
            <span key={t}>
              Tier {t}: <strong>{cnt}</strong>
            </span>
          ))}
        <span className="ml-auto flex gap-3">
          <span>
            풀 A: <strong className="text-indigo-600">{poolACnt}</strong>
          </span>
          <span>
            풀 B: <strong className="text-orange-600">{poolBCnt}</strong>
          </span>
          <span>
            리뷰 완료: <strong className="text-emerald-600">{reviewedCnt}</strong>/{total}
          </span>
        </span>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="text-center py-12 text-[var(--color-text-muted)] text-sm">
          키워드 로딩 중...
        </div>
      )}

      {/* Keyword grid */}
      {!isLoading && (
        <ExpertKeywordGrid
          keywords={keywords}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
      )}

      {/* Detail panel */}
      {panelData && (
        <ExpertKeywordDetail
          data={panelData}
          onReview={handleReview}
          onClose={() => setSelectedId(null)}
        />
      )}

      <div className="h-8 shrink-0" />
    </div>
  );
}
