import { formatPrice, parseJson, parseSizeRange } from "../utils/formatPrice";

export default function ProductDetail({ product, onClose }) {
  if (!product) return null;

  const colors = parseJson(product.colors);
  const materials = parseJson(product.materials);
  const sizes = parseJson(product.sizes);
  const images = parseJson(product.image_urls);
  const sizeRange = parseSizeRange(product.sizes);

  return (
    <div
      className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-md max-w-[720px] w-full max-h-[85vh] overflow-auto shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex">
          {/* Image */}
          <div className="w-[300px] shrink-0 bg-[#F0EFED]">
            {product.thumbnail_url ? (
              <img
                src={product.thumbnail_url}
                alt={product.product_name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-[400px] flex items-center justify-center text-[var(--color-text-muted)]">
                No Image
              </div>
            )}
          </div>

          {/* Info */}
          <div className="flex-1 p-6 flex flex-col gap-4">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[10px] font-semibold tracking-wider text-[var(--color-text-muted)] uppercase mb-1">
                  {product.brand_id}
                </p>
                <h2 className="font-['Lora'] text-xl font-semibold leading-tight">
                  {product.product_name}
                </h2>
              </div>
              <button
                onClick={onClose}
                className="text-[var(--color-text-muted)] hover:text-[var(--color-text)] text-xl leading-none"
              >
                &times;
              </button>
            </div>

            <p className="text-lg font-medium">
              {formatPrice(product.price, product.currency)}
            </p>

            {/* Colors */}
            {colors.length > 0 && (
              <div>
                <h4 className="text-[11px] font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">
                  Colors ({colors.length})
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {colors.map((c) => (
                    <span
                      key={c}
                      className="text-xs px-2 py-1 bg-[#F5F5F5] rounded-sm border border-[var(--color-border)]"
                    >
                      {c}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Sizes */}
            {sizes.length > 0 && (
              <div>
                <h4 className="text-[11px] font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">
                  Sizes ({sizeRange})
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {sizes.map((s) => (
                    <span
                      key={s}
                      className="text-xs px-2.5 py-1 bg-[#F5F5F5] rounded-sm border border-[var(--color-border)] text-center min-w-[36px]"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Fit */}
            {product.fit_info && (
              <div>
                <h4 className="text-[11px] font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-1">
                  Fit
                </h4>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  {product.fit_info}
                </p>
              </div>
            )}

            {/* Materials */}
            {materials.length > 0 && (
              <div>
                <h4 className="text-[11px] font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-1">
                  Materials
                </h4>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  {materials.join(", ")}
                </p>
              </div>
            )}

            {/* Description */}
            {product.description && (
              <div>
                <h4 className="text-[11px] font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-1">
                  Description
                </h4>
                <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed whitespace-pre-line">
                  {product.description}
                </p>
              </div>
            )}

            {/* Link */}
            {product.product_url && (
              <a
                href={product.product_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-[var(--color-primary)] hover:underline mt-auto"
              >
                View on official site &rarr;
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
