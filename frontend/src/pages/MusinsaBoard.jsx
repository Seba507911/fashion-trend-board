import { useQuery } from "@tanstack/react-query";
import { useState, useMemo } from "react";
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
    enabled: !!params.brand_slug || !!params.search || !!params.zoning,
  });
}

function useMusinsaStats() {
  return useQuery({
    queryKey: ["musinsa", "stats"],
    queryFn: () => api.get("/musinsa/stats").then(r => r.data),
  });
}

function useMusinsaZonings() {
  return useQuery({
    queryKey: ["musinsa", "zonings"],
    queryFn: () => api.get("/musinsa/zonings").then(r => r.data),
  });
}

/* ── Style grouping: merge color variants into one style ── */
function groupByStyle(products) {
  const groups = {};
  for (const p of products) {
    const key = `${p.brand_slug}::${p.style_name || p.product_name}`;
    if (!groups[key]) {
      groups[key] = {
        ...p,
        colorVariants: [],
      };
    }
    groups[key].colorVariants.push({
      color: p.color || "",
      product_name: p.product_name,
      product_url: p.product_url,
      image_url: p.image_url,
      price: p.price,
      id: p.id,
    });
  }
  return Object.values(groups);
}

function StyleCard({ style, onClick }) {
  const colorCount = style.colorVariants.length;
  return (
    <button
      onClick={() => onClick(style)}
      className="group bg-white border border-[var(--color-border)] rounded-lg overflow-hidden hover:shadow-md transition-shadow text-left w-full"
    >
      <div className="aspect-[3/4] bg-gray-100 overflow-hidden relative">
        {style.image_url ? (
          <img
            src={style.image_url}
            alt={style.style_name || style.product_name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
            onError={(e) => { e.target.style.display = "none"; }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-[var(--color-text-muted)] text-xs">No Image</div>
        )}
        {colorCount > 1 && (
          <div className="absolute top-2 right-2 bg-black/60 text-white text-[9px] px-1.5 py-0.5 rounded-full font-medium">
            {colorCount} colors
          </div>
        )}
      </div>
      <div className="p-3">
        <div className="text-[10px] font-semibold text-[var(--color-primary)] uppercase tracking-wide mb-0.5">
          {style.brand_name}
        </div>
        <div className="text-xs text-[var(--color-text)] font-medium leading-snug line-clamp-2 mb-1.5">
          {style.style_name || style.product_name}
        </div>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-sm font-bold text-[var(--color-text)]">
              {style.price?.toLocaleString()}원
            </span>
            {style.original_price > style.price && (
              <span className="text-[10px] text-[var(--color-text-muted)] line-through ml-1">
                {style.original_price?.toLocaleString()}
              </span>
            )}
          </div>
          {style.rating && (
            <span className="text-[10px] text-[var(--color-text-muted)]">
              ★ {style.rating}
            </span>
          )}
        </div>
        {/* Color dots */}
        {colorCount > 1 && (
          <div className="flex gap-1 mt-1.5 flex-wrap">
            {style.colorVariants.slice(0, 6).map((v, i) => (
              <span key={i} className="text-[8px] px-1.5 py-0.5 rounded bg-gray-100 text-[var(--color-text-muted)] truncate max-w-[60px]">
                {v.color || "기본"}
              </span>
            ))}
            {colorCount > 6 && (
              <span className="text-[8px] text-[var(--color-text-muted)]">+{colorCount - 6}</span>
            )}
          </div>
        )}
        <div className="flex gap-1.5 mt-1.5 flex-wrap">
          {style.season && (
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-600 font-medium">{style.season}</span>
          )}
          {style.gender && (
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-gray-100 text-[var(--color-text-muted)]">{style.gender}</span>
          )}
        </div>
      </div>
    </button>
  );
}

function StyleDetailModal({ style, onClose }) {
  if (!style) return null;

  const [selectedVariant, setSelectedVariant] = useState(0);

  let detailImages = [];
  try {
    detailImages = style.detail_images ? JSON.parse(style.detail_images) : [];
  } catch { /* ignore */ }

  const currentVariant = style.colorVariants[selectedVariant] || style.colorVariants[0];

  return (
    <div className="fixed inset-0 z-50 bg-black/60 flex items-start justify-center p-8 overflow-y-auto" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl max-w-[680px] w-full my-8" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-start justify-between p-5 border-b border-[var(--color-border)]">
          <div>
            <div className="text-[11px] font-semibold text-[var(--color-primary)] uppercase tracking-wide mb-1">
              {style.brand_name}
            </div>
            <h2 className="text-base font-bold text-[var(--color-text)] leading-snug">
              {style.style_name || style.product_name}
            </h2>
          </div>
          <button onClick={onClose} className="text-xs px-3 py-1.5 rounded border border-[var(--color-border)] hover:bg-gray-50 shrink-0 ml-4">
            닫기
          </button>
        </div>

        <div className="p-5">
          {/* Main Image */}
          {currentVariant.image_url && (
            <img src={currentVariant.image_url} alt={currentVariant.product_name} className="w-full rounded-lg mb-4" />
          )}

          {/* Color Range */}
          {style.colorVariants.length > 1 && (
            <div className="mb-4">
              <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">
                Colors ({style.colorVariants.length})
              </div>
              <div className="flex flex-wrap gap-1.5">
                {style.colorVariants.map((v, i) => (
                  <button
                    key={i}
                    onClick={() => setSelectedVariant(i)}
                    className={`text-xs px-2.5 py-1.5 rounded border transition-colors ${
                      i === selectedVariant
                        ? "border-[var(--color-primary)] bg-[var(--color-primary)]/5 text-[var(--color-primary)] font-medium"
                        : "border-[var(--color-border)] bg-[#F5F5F5] text-[var(--color-text-secondary)] hover:border-gray-400"
                    }`}
                  >
                    {v.color || "기본"}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Detail Images */}
          {detailImages.length > 0 && (
            <div className="mb-4">
              <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">
                상세 이미지 ({detailImages.length})
              </div>
              <div className="grid grid-cols-4 gap-2">
                {detailImages.map((img, i) => (
                  <img key={i} src={img} alt={`Detail ${i + 1}`}
                    className="w-full aspect-square object-cover rounded border border-[var(--color-border)]"
                    loading="lazy" onError={(e) => { e.target.style.display = "none"; }} />
                ))}
              </div>
            </div>
          )}

          {/* Product Info Grid */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            {[
              { label: "가격", value: style.price ? `${style.price.toLocaleString()}원` : "-" },
              { label: "정가", value: style.original_price ? `${style.original_price.toLocaleString()}원` : "-" },
              { label: "시즌", value: style.season || "-" },
              { label: "품번", value: style.product_code || "-" },
              { label: "성별", value: style.gender || "-" },
              { label: "컬러", value: style.colorVariants.length > 1 ? `${style.colorVariants.length}개 컬러` : (style.color || "-") },
              { label: "평점", value: style.rating ? `★ ${style.rating} (${style.review_count?.toLocaleString() || 0}건)` : "-" },
              { label: "조회수", value: style.view_count || "-" },
              { label: "누적판매", value: style.sell_count || "-" },
              { label: "할인율", value: style.sale_rate ? `${style.sale_rate}%` : "-" },
            ].map((item) => (
              <div key={item.label} className="flex justify-between text-xs py-1.5 border-b border-[var(--color-border)]/50">
                <span className="text-[var(--color-text-muted)]">{item.label}</span>
                <span className="text-[var(--color-text)] font-medium">{item.value}</span>
              </div>
            ))}
          </div>

          {/* Description */}
          {style.description && (
            <div className="mb-4">
              <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-1">설명</div>
              <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">{style.description}</p>
            </div>
          )}

          {/* External Link */}
          <a href={currentVariant.product_url || style.product_url} target="_blank" rel="noopener noreferrer"
            className="block text-center text-xs px-4 py-2.5 rounded-lg bg-[var(--color-primary)] text-white font-medium hover:opacity-90 transition-opacity">
            무신사에서 보기 →
          </a>
        </div>
      </div>
    </div>
  );
}

export default function MusinsaBoard() {
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [selectedZoning, setSelectedZoning] = useState(null);
  const [search, setSearch] = useState("");
  const [selectedStyle, setSelectedStyle] = useState(null);

  const { data: brands = [] } = useMusinsaBrands();
  const { data: stats } = useMusinsaStats();
  const { data: zonings = [] } = useMusinsaZonings();
  const { data: products = [], isLoading } = useMusinsaProducts({
    brand_slug: selectedBrand,
    zoning: selectedZoning,
    search: search.length >= 2 ? search : undefined,
  });

  // Group products by style (merge color variants)
  const styles = useMemo(() => groupByStyle(products), [products]);

  return (
    <main className="flex-1 flex flex-col overflow-hidden bg-[var(--color-bg)]">
      {/* Header */}
      <div className="shrink-0 bg-[var(--color-bg)] border-b border-[var(--color-border)] px-8 pt-6 pb-4">
        <div className="max-w-[1200px] mx-auto">
          <div className="flex items-center gap-2 mb-1">
            <h1 className="font-['Lora'] text-xl font-semibold tracking-wide">Musinsa</h1>
            <span className="text-[10px] px-2 py-0.5 rounded bg-amber-100 text-amber-700 font-medium">Data check</span>
          </div>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            무신사 브랜드 상품 수집
            {stats && (
              <span className="ml-2 text-[var(--color-text-muted)]">
                &middot; {stats.total_brands} brands &middot; {stats.total_products} products
              </span>
            )}
            {products.length > 0 && (
              <span className="ml-2 text-[var(--color-text-muted)]">
                &middot; {styles.length} styles (컬러 그루핑)
              </span>
            )}
          </p>

          <div className="flex gap-2 mt-3 items-center flex-wrap">
            {/* Zoning Filter */}
            <select
              value={selectedZoning || ""}
              onChange={(e) => { setSelectedZoning(e.target.value || null); setSelectedBrand(null); setSearch(""); }}
              className="text-xs px-3 py-2 border border-[var(--color-border)] rounded-md bg-white text-[var(--color-text)]"
            >
              <option value="">전체 조닝</option>
              {zonings.map(z => (
                <option key={z.zoning} value={z.zoning}>{z.zoning} ({z.brands})</option>
              ))}
            </select>

            <button
              onClick={() => { setSelectedBrand(null); setSelectedZoning(null); setSearch(""); }}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                !selectedBrand && !selectedZoning && !search ? "bg-gray-800 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              All ({stats?.total_products || 0})
            </button>
            {brands.filter(b => !selectedZoning || products.some(p => p.brand_slug === b.brand_slug)).slice(0, 20).map(b => (
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
            {brands.length > 20 && !selectedZoning && (
              <span className="text-[10px] text-[var(--color-text-muted)]">+{brands.length - 20} more</span>
            )}
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
          ) : styles.length === 0 ? (
            <p className="text-sm text-[var(--color-text-muted)] py-10 text-center">
              {selectedBrand || search ? "No products found" : "브랜드를 선택하거나 검색어를 입력하세요"}
            </p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {styles.map(s => (
                <StyleCard key={s.id} style={s} onClick={setSelectedStyle} />
              ))}
            </div>
          )}
        </div>
      </div>

      <StyleDetailModal style={selectedStyle} onClose={() => setSelectedStyle(null)} />
    </main>
  );
}
