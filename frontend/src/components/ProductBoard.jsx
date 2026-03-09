import { useState } from "react";
import { useProducts, useCategories } from "../hooks/useProducts";
import ProductCard from "./ProductCard";
import ProductDetail from "./ProductDetail";

export default function ProductBoard({ selectedBrand }) {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const { data: categories = [] } = useCategories();
  const { data: products = [], isLoading } = useProducts({
    brand: selectedBrand,
    category: selectedCategory,
  });

  const subCategories = categories.filter((c) => c.parent_id);

  // 카테고리별 그룹핑
  const grouped = {};
  for (const p of products) {
    const catId = p.category_id || "uncategorized";
    if (!grouped[catId]) grouped[catId] = [];
    grouped[catId].push(p);
  }

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
        Object.entries(grouped).map(([catId, catProducts]) => (
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
        ))
      )}

      {/* Product Detail Modal */}
      <ProductDetail
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
      />
    </main>
  );
}
