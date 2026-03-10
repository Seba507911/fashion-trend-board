import { useLocation, useNavigate } from "react-router-dom";
import { useBrands } from "../hooks/useProducts";

export default function Sidebar({ selectedBrand, onBrandSelect }) {
  const { data: brands = [] } = useBrands();
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = [
    { id: "runway", label: "Runway", path: "/runway" },
    { id: "trend-flow", label: "Trend Flow", path: "/flow" },
    { id: "market-brand-board", label: "Market Brand Board", path: "/" },
    { id: "trend-analysis", label: "Trend Analysis", path: "/trend" },
    { id: "graph-view", label: "Graph View", path: "/graph" },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <aside className="w-[220px] min-h-screen border-r border-[var(--color-border)] bg-[var(--color-sidebar)] p-6 flex flex-col gap-5 shrink-0">
      <div
        className="flex items-center gap-2 cursor-pointer"
        onClick={() => navigate("/")}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2">
          <path d="M12 3l1.5 4.5H18l-3.5 2.5L16 14.5 12 12l-4 2.5 1.5-4.5L6 7.5h4.5z" />
        </svg>
        <span className="font-['Lora'] text-lg font-medium tracking-widest">FTIB</span>
      </div>

      <hr className="border-[var(--color-border)]" />

      <nav className="flex flex-col gap-0.5">
        <span className="text-[10px] font-semibold tracking-[1.5px] text-[var(--color-text-muted)] mb-1">
          DASHBOARD
        </span>

        {navItems.map((item) => (
          <div key={item.id}>
            <button
              onClick={() => navigate(item.path)}
              className={`w-full text-left px-2.5 py-2 text-[13px] rounded-sm flex items-center gap-2.5 ${
                isActive(item.path)
                  ? "bg-[var(--color-primary)]/8 text-[var(--color-primary)] font-medium border-l-2 border-[var(--color-primary)]"
                  : "text-[var(--color-text-secondary)] hover:bg-black/3"
              }`}
            >
              {item.label}
            </button>

            {item.id === "market-brand-board" && isActive("/") && (
              <div className="flex flex-col gap-0.5 mt-1">
                <button
                  onClick={() => onBrandSelect(null)}
                  className={`pl-8 pr-2.5 py-1.5 text-xs flex items-center gap-2.5 rounded-sm ${
                    selectedBrand === null
                      ? "bg-[var(--color-primary)]/5 text-[var(--color-primary)] font-medium"
                      : "text-[var(--color-text-secondary)] hover:bg-black/3"
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full ${selectedBrand === null ? "bg-[var(--color-primary)]" : "bg-[var(--color-text-muted)]"}`} />
                  All Brands
                </button>
                {brands.map((brand) => (
                  <button
                    key={brand.id}
                    onClick={() => onBrandSelect(brand.id)}
                    className={`pl-8 pr-2.5 py-1.5 text-xs flex items-center gap-2.5 rounded-sm overflow-hidden ${
                      selectedBrand === brand.id
                        ? "bg-[var(--color-primary)]/5 text-[var(--color-primary)] font-medium"
                        : "text-[var(--color-text-secondary)] hover:bg-black/3"
                    }`}
                  >
                    <span className={`w-2 h-2 rounded-full shrink-0 ${selectedBrand === brand.id ? "bg-[var(--color-primary)]" : "bg-[var(--color-text-muted)]"}`} />
                    <span className="truncate">{brand.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>
    </aside>
  );
}
