import { formatPrice, getScoreBadge, parseSizeRange, parseJson } from "../utils/formatPrice";

export default function ProductCard({ product, onClick }) {
  const score = product.total_score ?? Math.floor(Math.random() * 100);
  const badge = getScoreBadge(score);
  const colors = parseJson(product.colors);
  const tags = parseJson(product.style_tags);
  const sizeRange = parseSizeRange(product.sizes);

  return (
    <div
      className="border border-[var(--color-border)] rounded-sm overflow-hidden bg-[var(--color-card)] hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onClick?.(product)}
    >
      {/* Image */}
      <div className="relative aspect-[2/3] bg-[#F0EFED] overflow-hidden">
        {product.thumbnail_url ? (
          <img
            src={product.thumbnail_url}
            alt={product.product_name}
            className="w-full h-full object-cover object-top"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-[var(--color-text-muted)] text-xs">
            No Image
          </div>
        )}
        <span
          className="absolute top-2 left-2 text-white text-[10px] font-semibold px-2 py-0.5 rounded-sm"
          style={{ backgroundColor: badge.color }}
        >
          {score}
        </span>
        <span className="absolute bottom-2 left-2 text-[9px] font-semibold tracking-wider text-white/60 uppercase">
          {product.brand_id}
        </span>
      </div>

      {/* Info */}
      <div className="p-2.5 flex flex-col gap-1">
        <h3 className="font-['Lora'] text-[13px] font-medium leading-tight line-clamp-2">
          {product.product_name}
        </h3>
        <p className="text-[11px] font-medium">
          {formatPrice(product.price, product.currency)}
        </p>

        {/* Colors & Size Range */}
        <div className="flex items-center justify-between mt-0.5">
          <div className="flex items-center gap-1">
            {colors.length > 0 && (
              <span className="text-[9px] text-[var(--color-text-muted)]">
                {colors.length} {colors.length === 1 ? "color" : "colors"}
              </span>
            )}
          </div>
          {sizeRange && (
            <span className="text-[9px] text-[var(--color-text-muted)]">
              {sizeRange}
            </span>
          )}
        </div>

        {/* Tags */}
        {tags.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            {tags.slice(0, 2).map((tag) => (
              <span
                key={tag}
                className="text-[9px] px-1.5 py-0.5 bg-black/5 rounded-sm text-[var(--color-text-secondary)]"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
