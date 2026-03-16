import { useState, useMemo } from "react";
import { CATEGORY_MAP } from "../components/trendflow/mockData";
import { useTrendFlowKeywords, useTrendFlowKeywordDetail } from "../hooks/useTrendFlowCheck";
import FilterBar from "../components/trendflow/FilterBar";
import CategoryTabs from "../components/trendflow/CategoryTabs";
import KeywordGrid from "../components/trendflow/KeywordGrid";
import KeywordDetailPanel from "../components/trendflow/KeywordDetailPanel";
import MatrixView from "../components/trendflow/MatrixView";
import TimelineView from "../components/trendflow/TimelineView";

export default function TrendFlowCheck() {
  // Level 1: Filters
  const [season, setSeason] = useState("26SS");
  const [zoning, setZoning] = useState("전체");

  // Level 2: Category + View
  const [category, setCategory] = useState("전체");
  const [view, setView] = useState("card");

  // Level 3-4: Selection
  const [selectedId, setSelectedId] = useState(null);

  // API category param (null means all)
  const apiCategory = CATEGORY_MAP[category] === "all" ? undefined : CATEGORY_MAP[category];

  // Fetch keywords from backend
  const { data: apiData, isLoading } = useTrendFlowKeywords({
    season,
    category: apiCategory,
  });

  const keywords = apiData?.keywords || [];

  // Find selected keyword from fetched data
  const selectedKeyword = selectedId
    ? keywords.find((kw) => kw.id === selectedId)
    : null;

  // Fetch detail for selected keyword (timeline + brand distribution)
  const { data: detailData } = useTrendFlowKeywordDetail({
    keyword: selectedKeyword?.keyword,
    season,
  });

  // Merge detail data into selectedKeyword for the panel
  const panelData = useMemo(() => {
    if (!selectedKeyword) return null;

    // Build timeline from detail API
    const timeline = detailData?.timeline?.map((t) => ({
      season: t.season,
      strength: Math.min(100, Math.round((t.runway_count / 30) * 100)),
      label: `런웨이 ${t.runway_count}회 · ${t.designer_count} 디자이너`,
    })) || [];

    // Use detail brands if available, fallback to keyword-level brands
    const brands = detailData?.brands?.length
      ? detailData.brands
      : selectedKeyword.brands;

    return {
      ...selectedKeyword,
      signalDetails: selectedKeyword.signal_details,
      timeline,
      brands,
    };
  }, [selectedKeyword, detailData]);

  return (
    <main className="flex-1 flex flex-col overflow-hidden bg-[var(--color-bg)]">
      {/* Sticky Header */}
      <div className="shrink-0 bg-[var(--color-bg)] border-b border-[var(--color-border)] px-8 pt-6 pb-0">
        <div className="max-w-[1200px] mx-auto">
          <h1 className="font-['Lora'] text-xl font-semibold tracking-wide mb-1">
            Trend Flow <span className="text-sm font-normal text-[var(--color-text-muted)]">check(Test)</span>
          </h1>
          <p className="text-sm text-[var(--color-text-secondary)] mb-5">
            VLM 라벨 + 마켓 매칭 실데이터 기반 트렌드 키워드 대시보드
          </p>

          {/* Level 1: Filter Bar */}
          <div className="mb-4">
            <FilterBar
              season={season}
              setSeason={(s) => { setSeason(s); setSelectedId(null); }}
              zoning={zoning}
              setZoning={setZoning}
            />
          </div>

          {/* Level 2: Category Tabs + View Toggle */}
          <CategoryTabs
            category={category}
            setCategory={(c) => { setCategory(c); setSelectedId(null); }}
            view={view}
            setView={setView}
          />
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        <div className="max-w-[1200px] mx-auto">
          {/* Result count + data source info */}
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs text-[var(--color-text-muted)]">
              {keywords.length}개 키워드 · {season} · {zoning}
              {apiData && (
                <span className="ml-2 text-[var(--color-text-muted)]">
                  (VLM {apiData.total_vlm_looks}룩 · 마켓 {apiData.total_products}상품)
                </span>
              )}
            </span>
            {isLoading && (
              <span className="text-xs text-[var(--color-primary)]">Loading...</span>
            )}
          </div>

          {/* No data state */}
          {!isLoading && keywords.length === 0 && (
            <div className="text-center py-20 text-[var(--color-text-muted)]">
              <p className="text-sm mb-1">해당 시즌의 VLM 라벨 데이터가 없습니다</p>
              <p className="text-xs">현재 26SS / 26FW 시즌만 VLM 라벨이 존재합니다</p>
            </div>
          )}

          {/* Level 3: View content */}
          {view === "card" && keywords.length > 0 && (
            <KeywordGrid
              keywords={keywords}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          )}

          {view === "matrix" && keywords.length > 0 && (
            <MatrixView
              keywords={keywords}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          )}

          {view === "timeline" && keywords.length > 0 && (
            <TimelineView
              keywords={keywords}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          )}

          {/* Level 4: Detail Panel */}
          {panelData && (
            <KeywordDetailPanel
              data={panelData}
              season={season}
              onClose={() => setSelectedId(null)}
            />
          )}

          <div className="h-8" />
        </div>
      </div>
    </main>
  );
}
