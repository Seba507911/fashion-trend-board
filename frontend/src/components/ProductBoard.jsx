import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useProducts, useCategories, useTrendChips } from "../hooks/useProducts";
import ProductCard from "./ProductCard";
import ProductDetail from "./ProductDetail";

const CATEGORY_ORDER = ["outer", "inner", "bottom", "wear_etc", "headwear", "bag", "shoes", "acc_etc"];

const CHIP_CATEGORY_COLORS = {
  color: { bg: "bg-rose-50", text: "text-rose-700", border: "border-rose-200", dot: "bg-rose-400" },
  material: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200", dot: "bg-emerald-400" },
  silhouette: { bg: "bg-violet-50", text: "text-violet-700", border: "border-violet-200", dot: "bg-violet-400" },
};

function TrendChip({ chip, isActive, onClick }) {
  const style = CHIP_CATEGORY_COLORS[chip.category] || CHIP_CATEGORY_COLORS.color;
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[11px] transition-all ${
        isActive
          ? "border-[var(--color-primary)] bg-[var(--color-primary)] text-white font-medium"
          : `${style.border} ${style.bg} ${style.text} hover:shadow-sm`
      }`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${isActive ? "bg-white" : style.dot}`} />
      {chip.keyword}
      <span className={`text-[9px] ${isActive ? "text-white/70" : "opacity-50"}`}>
        {chip.market_count}
      </span>
    </button>
  );
}

export default function ProductBoard({ selectedBrand }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const keywordParam = searchParams.get("keyword");
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showTrendChips, setShowTrendChips] = useState(true);
  const { data: categories = [] } = useCategories();
  const { data: trendData } = useTrendChips("26SS");
  const { data: products = [], isLoading } = useProducts({
    brand: selectedBrand,
    category: selectedCategory,
    keyword: keywordParam,
  });

  const subCategories = categories.filter((c) => c.parent_id).sort((a, b) => {
    const ia = CATEGORY_ORDER.indexOf(a.id);
    const ib = CATEGORY_ORDER.indexOf(b.id);
    return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
  });

  // 카테고리별 그룹핑
  const grouped = {};
  for (const p of products) {
    const catId = p.category_id || "uncategorized";
    if (!grouped[catId]) grouped[catId] = [];
    grouped[catId].push(p);
  }

  const sortedCatKeys = Object.keys(grouped).sort((a, b) => {
    const ia = CATEGORY_ORDER.indexOf(a);
    const ib = CATEGORY_ORDER.indexOf(b);
    return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
  });

  const categoryLabel = (catId) => {
    const cat = categories.find((c) => c.id === catId);
    return cat ? cat.name_kr || cat.name : catId;
  };

  const trendChips = trendData?.chips || [];

  const handleChipClick = (keyword) => {
    if (keywordParam === keyword) {
      setSearchParams({});
    } else {
      setSearchParams({ keyword });
    }
  };

  return (
    <main className="flex-1 p-7 overflow-auto">
      <header className="mb-4">
        <h1 className="font-['Lora'] text-2xl font-semibold">Market Brand Board</h1>
        <p className="text-sm text-[var(--color-text-muted)] mt-1">
          {selectedBrand ? `${selectedBrand.toUpperCase()} — ` : ""}
          {products.length} Products
          {keywordParam && (
            <span className="ml-2">
              · filtered by <span className="text-[var(--color-primary)] font-medium">{keywordParam}</span>
            </span>
          )}
        </p>
      </header>

      {/* Trend Keyword Chips */}
      {trendChips.length > 0 && (
        <div className="mb-5">
          <button
            onClick={() => setShowTrendChips(!showTrendChips)}
            className="text-[10px] font-semibold tracking-[1.5px] text-[var(--color-text-muted)] mb-2 flex items-center gap-1 hover:text-[var(--color-text-secondary)]"
          >
            <span className="text-[9px]">{showTrendChips ? "▾" : "▸"}</span>
            RUNWAY TREND KEYWORDS
            <span className="font-normal tracking-normal ml-1">
              ({trendData?.vlm_looks || 0} runway looks → {trendData?.total_products || 0} market products)
            </span>
          </button>
          {showTrendChips && (
            <div className="flex flex-wrap gap-1.5">
              {keywordParam && (
                <button
                  onClick={() => setSearchParams({})}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full border border-[var(--color-border)] text-[11px] text-[var(--color-text-muted)] hover:bg-gray-50"
                >
                  Clear filter
                </button>
              )}
              {trendChips.map((chip) => (
                <TrendChip
                  key={chip.keyword}
                  chip={chip}
                  isActive={keywordParam === chip.keyword}
                  onClick={() => handleChipClick(chip.keyword)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Category Tabs */}
      <div className="flex gap-0 border-b border-[var(--color-border)] mb-6">
        <button
          onClick={() => setSelectedCategory(null)}
          className={`px-4 h-9 text-xs font-medium border-b-2 transition-colors ${
            selectedCategory === null
              ? "border-[var(--color-primary)] text-[var(--color-primary)]"
              : "border-transparent text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
          }`}
        >
          ALL
        </button>
        {subCategories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-4 h-9 text-xs font-medium border-b-2 transition-colors ${
              selectedCategory === cat.id
                ? "border-[var(--color-primary)] text-[var(--color-primary)]"
                : "border-transparent text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-sm text-[var(--color-text-muted)]">Loading...</p>
      ) : products.length === 0 ? (
        <div className="text-center py-20 text-[var(--color-text-muted)]">
          <p className="text-lg mb-2">
            {keywordParam ? `"${keywordParam}" 매칭 상품 없음` : "No products yet"}
          </p>
          <p className="text-sm">
            {keywordParam ? "다른 트렌드 키워드를 선택해보세요" : "Run a crawl to populate product data"}
          </p>
        </div>
      ) : selectedCategory ? (
        <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6 lg:grid-cols-7 xl:grid-cols-8 gap-2.5">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} onClick={setSelectedProduct} />
          ))}
        </div>
      ) : (
        sortedCatKeys.map((catId) => { const catProducts = grouped[catId]; return (
          <section key={catId} className="mb-8">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold">
                {categoryLabel(catId)}{" "}
                <span className="text-[var(--color-text-muted)] font-normal ml-1">
                  {catProducts.length}
                </span>
              </h2>
            </div>
            <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6 lg:grid-cols-7 xl:grid-cols-8 gap-2.5">
              {catProducts.map((p) => (
                <ProductCard key={p.id} product={p} onClick={setSelectedProduct} />
              ))}
            </div>
          </section>
        ); })
      )}

      {/* Product Detail Modal */}
      <ProductDetail
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
      />
    </main>
  );
}
