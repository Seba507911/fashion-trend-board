export function formatPrice(price, currency = "KRW") {
  if (!price) return "";
  if (currency === "USD") return `$${Number(price).toLocaleString()}`;
  if (currency === "EUR") return `€${Number(price).toLocaleString()}`;
  if (currency === "JPY") return `¥${Number(price).toLocaleString()}`;
  return `₩${Number(price).toLocaleString()}`;
}

export function getScoreBadge(score) {
  if (score >= 90) return { label: "Hot", color: "var(--color-badge-hot)" };
  if (score >= 70) return { label: "Rising", color: "var(--color-badge-rising)" };
  if (score >= 50) return { label: "Mod", color: "var(--color-badge-moderate)" };
  if (score >= 30) return { label: "Low", color: "var(--color-badge-low)" };
  return { label: "Cold", color: "var(--color-badge-cold)" };
}

export function parseSizeRange(sizesJson) {
  try {
    const sizes = typeof sizesJson === "string" ? JSON.parse(sizesJson || "[]") : sizesJson || [];
    if (sizes.length === 0) return "";
    if (sizes.length === 1) return sizes[0];
    return `${sizes[0]}~${sizes[sizes.length - 1]}`;
  } catch {
    return "";
  }
}

export function parseJson(jsonStr) {
  try {
    return typeof jsonStr === "string" ? JSON.parse(jsonStr || "[]") : jsonStr || [];
  } catch {
    return [];
  }
}
