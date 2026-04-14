import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

function useMusinsaBrands() {
  return useQuery({
    queryKey: ["musinsa", "brands"],
    queryFn: () => api.get("/musinsa/brands").then(r => r.data),
  });
}

function useMusinsaProducts(params) {
  return useQuery({
    queryKey: ["musinsa", "products", params],
    queryFn: () => api.get("/musinsa/products", { params }).then(r => r.data),
    enabled: !!params.brand_slug || !!params.search,
  });
}

function useMusinsaStats() {
  return useQuery({
    queryKey: ["musinsa", "stats"],
    queryFn: () => api.get("/musinsa/stats").then(r => r.data),
  });
}

function ProductCard({ product, onClick }) {
  return (
    <button
      onClick={() => onClick(product)}
      className="group bg-white border border-[var(--color-border)] rounded-lg overflow-hidden hover:shadow-md transition-shadow text-left w-full"
    >
      <div className="aspect-[3/4] bg-gray-100 overflow-hidden">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.product_name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
            onError={(e) => { e.target.style.display = "none"; }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-[var(--color-text-muted)] text-xs">No Image</div>
        )}
      </div>
      <div className="p-3">
        <div className="text-[10px] font-semibold text-[var(--color-primary)] uppercase tracking-wide mb-0.5">
          {product.brand_name}
        </div>
        <div className="text-xs text-[var(--color-text)] font-medium leading-snug line-clamp-2 mb-1.5">
          {product.product_name}
        </div>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-sm font-bold text-[var(--color-text)]">
              {product.price?.toLocaleString()}원
            </span>
            {product.original_price > product.price && (
              <span className="text-[10px] text-[var(--color-text-muted)] line-through ml-1">
                {product.original_price?.toLocaleString()}
              </span>
            )}
          </div>
          {product.rating && (
            <span className="text-[10px] text-[var(--color-text-muted)]">
              ★ {product.rating}
            </span>
          )}
        </div>
        <div className="flex gap-1.5 mt-1.5 flex-wrap">
          {product.season && (
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-600 font-medium">{product.season}</span>
          )}
          {product.gender && (
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-gray-100 text-[var(--color-text-muted)]">{product.gender}</span>
          )}
          {product.color && (
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-gray-100 text-[var(--color-text-muted)]">{product.color}</span>
          )}
        </div>
      </div>
    </button>
  );
}

function ProductDetailModal({ product, onClose }) {
  if (!product) return null;

  let detailImages = [];
  try {
    detailImages = product.detail_images ? JSON.parse(product.detail_images) : [];
  } catch { /* ignore */ }

  return (
    <div className="fixed inset-0 z-50 bg-black/60 flex items-start justify-center p-8 overflow-y-auto" onClick={onClose}>
      <div
        className="bg-white rounded-xl shadow-2xl max-w-[680px] w-full my-8"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-5 border-b border-[var(--color-border)]">
          <div>
            <div className="text-[11px] font-semibold text-[var(--color-primary)] uppercase tracking-wide mb-1">
              {product.brand_name}
            </div>
            <h2 className="text-base font-bold text-[var(--color-text)] leading-snug">
              {product.product_name}
            </h2>
          </div>
          <button onClick={onClose} className="text-xs px-3 py-1.5 rounded border border-[var(--color-border)] hover:bg-gray-50 shrink-0 ml-4">
            닫기
          </button>
        </div>

        {/* Main Image + Detail Images */}
        <div className="p-5">
          {product.image_url && (
            <img src={product.image_url} alt={product.product_name} className="w-full rounded-lg mb-4" />
          )}

          {detailImages.length > 0 && (
            <div className="mb-4">
              <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">
                상세 이미지 ({detailImages.length})
              </div>
              <div className="grid grid-cols-4 gap-2">
                {detailImages.map((img, i) => (
                  <img
                    key={i}
                    src={img}
                    alt={`Detail ${i + 1}`}
                    className="w-full aspect-square object-cover rounded border border-[var(--color-border)]"
                    loading="lazy"
                    onError={(e) => { e.target.style.display = "none"; }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Product Info Grid */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            {[
              { label: "가격", value: product.price ? `${product.price.toLocaleString()}원` : "-" },
              { label: "정가", value: product.original_price ? `${product.original_price.toLocaleString()}원` : "-" },
              { label: "할인율", value: product.sale_rate ? `${product.sale_rate}%` : "-" },
              { label: "시즌", value: product.season || "-" },
              { label: "품번", value: product.product_code || "-" },
              { label: "성별", value: product.gender || "-" },
              { label: "컬러", value: product.color || "-" },
              { label: "평점", value: product.rating ? `★ ${product.rating} (${product.review_count?.toLocaleString() || 0}건)` : "-" },
              { label: "조회수", value: product.view_count || "-" },
              { label: "누적판매", value: product.sell_count || "-" },
            ].map((item) => (
              <div key={item.label} className="flex justify-between text-xs py-1.5 border-b border-[var(--color-border)]/50">
                <span className="text-[var(--color-text-muted)]">{item.label}</span>
                <span className="text-[var(--color-text)] font-medium">{item.value}</span>
              </div>
            ))}
          </div>

          {/* Description */}
          {product.description && (
            <div className="mb-4">
              <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-1">설명</div>
              <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">{product.description}</p>
            </div>
          )}

          {/* External Link */}
          <a
            href={product.product_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block text-center text-xs px-4 py-2.5 rounded-lg bg-[var(--color-primary)] text-white font-medium hover:opacity-90 transition-opacity"
          >
            무신사에서 보기 →
          </a>
        </div>
      </div>
    </div>
  );
}

export default function MusinsaBoard() {
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [search, setSearch] = useState("");
  const [selectedProduct, setSelectedProduct] = useState(null);

  const { data: brands = [] } = useMusinsaBrands();
  const { data: stats } = useMusinsaStats();
  const { data: products = [], isLoading } = useMusinsaProducts({
    brand_slug: selectedBrand,
    search: search.length >= 2 ? search : undefined,
  });

  return (
    <main className="flex-1 flex flex-col overflow-hidden bg-[var(--color-bg)]">
      {/* Header */}
      <div className="shrink-0 bg-[var(--color-bg)] border-b border-[var(--color-border)] px-8 pt-6 pb-4">
        <div className="max-w-[1200px] mx-auto">
          <h1 className="font-['Lora'] text-xl font-semibold tracking-wide mb-1">Musinsa</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            무신사 브랜드 상품 수집
            {stats && (
              <span className="ml-2 text-[var(--color-text-muted)]">
                &middot; {stats.total_brands} brands &middot; {stats.total_products} products
              </span>
            )}
          </p>

          <div className="flex gap-2 mt-3 items-center flex-wrap">
            <button
              onClick={() => { setSelectedBrand(null); setSearch(""); }}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                !selectedBrand && !search ? "bg-gray-800 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              All ({stats?.total_products || 0})
            </button>
            {brands.map(b => (
              <button
                key={b.brand_slug}
                onClick={() => { setSelectedBrand(b.brand_slug); setSearch(""); }}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                  selectedBrand === b.brand_slug
                    ? "bg-[var(--color-primary)] text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {b.brand_name} ({b.cnt})
              </button>
            ))}
            <input
              type="text"
              placeholder="상품명 검색..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); if (e.target.value.length >= 2) setSelectedBrand(null); }}
              className="ml-auto text-xs px-3 py-2 border border-[var(--color-border)] rounded-md w-48 bg-white"
            />
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        <div className="max-w-[1200px] mx-auto">
          {isLoading ? (
            <p className="text-sm text-[var(--color-text-muted)] py-10 text-center">Loading...</p>
          ) : products.length === 0 ? (
            <p className="text-sm text-[var(--color-text-muted)] py-10 text-center">
              {selectedBrand || search ? "No products found" : "브랜드를 선택하거나 검색어를 입력하세요"}
            </p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {products.map(p => (
                <ProductCard key={p.id} product={p} onClick={setSelectedProduct} />
              ))}
            </div>
          )}
        </div>
      </div>

      <ProductDetailModal product={selectedProduct} onClose={() => setSelectedProduct(null)} />
    </main>
  );
}
