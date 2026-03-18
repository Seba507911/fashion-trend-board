import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useProducts, useCategories } from "../hooks/useProducts";
import ProductCard from "./ProductCard";
import ProductDetail from "./ProductDetail";

export default function ProductBoard({ selectedBrand }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const keywordParam = searchParams.get("keyword");
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const { data: categories = [] } = useCategories();
  const { data: products = [], isLoading } = useProducts({
    brand: selectedBrand,
    category: selectedCategory,
    keyword: keywordParam,
  });

  // 카테고리 표시 순서
  const CATEGORY_ORDER = ["outer", "inner", "bottom", "wear_etc", "headwear", "bag", "shoes", "acc_etc"];

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

  // 정렬된 카테고리 키
  const sortedCatKeys = Object.keys(grouped).sort((a, b) => {
    const ia = CATEGORY_ORDER.indexOf(a);
    const ib = CATEGORY_ORDER.indexOf(b);
    return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
  });

  const categoryLabel = (catId) => {
    const cat = categories.find((c) => c.id === catId);
    return cat ? cat.name_kr || cat.name : catId;
  };

  return (
    <main className="flex-1 p-7 overflow-auto">
      <header className="mb-6">
        <h1 className="font-['Lora'] text-2xl font-semibold">Market Brand Board</h1>
        <p className="text-sm text-[var(--color-text-muted)] mt-1">
          {selectedBrand ? `${selectedBrand.toUpperCase()} — ` : ""}
          {products.length} Products
        </p>
        {keywordParam && (
          <div className="mt-2 flex items-center gap-2">
            <span className="text-xs px-2.5 py-1 rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)] font-medium">
              keyword: {keywordParam}
            </span>
            <button
              onClick={() => setSearchParams({})}
              className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text)] underline"
            >
              Clear
            </button>
          </div>
        )}
      </header>

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
          <p className="text-lg mb-2">No products yet</p>
          <p className="text-sm">Run a crawl to populate product data</p>
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
