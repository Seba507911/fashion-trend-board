import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useBrands } from "../hooks/useProducts";

/* ── Brand hierarchy: zoning → region → brand_ids ── */
/* Only brands with collected products are shown in main groups */
const BRAND_GROUPS = [
  {
    zoning: "럭셔리 / 컨템포러리",
    groups: [
      { region: "Global", ids: ["lemaire", "acne_studios", "bode", "nanushka", "toteme", "therow", "ami"] },
      { region: "Korea", ids: [] },
    ],
  },
  {
    zoning: "스포츠 / 아웃도어",
    groups: [
      { region: "Global", ids: ["nike", "newbalance", "on_running", "lululemon", "alo", "skims", "patagonia"] },
      { region: "Korea", ids: ["descente", "northface", "kolonsport", "fila"] },
    ],
  },
  {
    zoning: "캐주얼 / 스트리트",
    groups: [
      { region: "Global", ids: ["ralph_lauren", "stussy", "supreme"] },
      { region: "Korea", ids: ["youth", "marithe", "coor", "blankroom", "mardi", "thisisneverthat", "emis", "depound", "covernat"] },
    ],
  },
  {
    zoning: "SPA / 매스",
    groups: [
      { region: "Global", ids: ["zara", "hm"] },
    ],
  },
  {
    zoning: "일본 컨템포러리",
    groups: [
      { region: "Japan", ids: ["nanamica"] },
    ],
  },
];

/* TBA: registered but not yet collected */
const TBA_BRAND_IDS = [
  "jacquemus", "maison_kitsune", "wooyoungmi", "ader_error", "dunst", "amomento", "recto",
  "hoka", "salomon", "k2", "blackyak", "cos", "uniqlo",
  "carhartt_wip", "captain_sunshine", "comoli", "danton", "auralee", "apresse", "visvim", "kapital",
  "newera", "kangol", "snowpeak",
  "palace", "goldwin", "rrl",
];

// Flatten all known brand IDs for grouping
const KNOWN_IDS = new Set([
  ...BRAND_GROUPS.flatMap(z => z.groups.flatMap(g => g.ids)),
  ...TBA_BRAND_IDS,
]);

export default function Sidebar({ selectedBrand, onBrandSelect }) {
  const { data: brands = [] } = useBrands();
  const location = useLocation();
  const navigate = useNavigate();
  const [expandedZoning, setExpandedZoning] = useState(null);

  const navItems = [
    { id: "briefing", label: "Project Briefing", path: "/" },
    { id: "trend-flow", label: "Trend Flow", path: "/flow" },
    { id: "trend-flow-check", label: "Trend Flow check(Test)", path: "/flow-check" },
    { id: "runway", label: "Runway", path: "/runway", bold: true },
    { id: "vlm-viewer", label: "Runway(VLM Test)", path: "/vlm", bold: true },
    { id: "market-brand-board", label: "Market Brand Board", path: "/market", bold: true },
    { id: "trend-analysis", label: "Trend Analysis", path: "/trend" },
    { id: "graph-view", label: "Graph View", path: "/graph" },
  ];

  const isActive = (path) => location.pathname === path;

  // Build brand lookup map
  const brandMap = {};
  brands.forEach(b => { brandMap[b.id] = b; });

  // Brands not in any group (ungrouped)
  const ungroupedBrands = brands.filter(b => !KNOWN_IDS.has(b.id));

  const toggleZoning = (zoning) => {
    setExpandedZoning(expandedZoning === zoning ? null : zoning);
  };

  const BrandButton = ({ brandId }) => {
    const brand = brandMap[brandId];
    if (!brand) return null;
    return (
      <button
        onClick={() => onBrandSelect(brand.id)}
        className={`pl-10 pr-2.5 py-1 text-[11px] flex items-center gap-2 rounded-sm overflow-hidden ${
          selectedBrand === brand.id
            ? "bg-[var(--color-primary)]/5 text-[var(--color-primary)] font-medium"
            : "text-[var(--color-text-secondary)] hover:bg-black/3"
        }`}
      >
        <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${selectedBrand === brand.id ? "bg-[var(--color-primary)]" : "bg-[var(--color-text-muted)]"}`} />
        <span className="truncate">{brand.name}</span>
      </button>
    );
  };

  return (
    <aside className="w-[220px] min-h-screen border-r border-[var(--color-border)] bg-[var(--color-sidebar)] p-6 flex flex-col gap-5 shrink-0 overflow-y-auto">
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
                  ? "bg-[var(--color-primary)]/8 text-[var(--color-primary)] font-semibold border-l-2 border-[var(--color-primary)]"
                  : item.bold
                    ? "text-[var(--color-text)] font-semibold hover:bg-black/3"
                    : "text-[var(--color-text-secondary)] hover:bg-black/3"
              }`}
            >
              {item.label}
            </button>

            {/* Brand Board 하위: 조닝별 브랜드 계층 */}
            {item.id === "market-brand-board" && isActive("/market") && (
              <div className="flex flex-col gap-0 mt-1">
                {/* All Brands */}
                <button
                  onClick={() => onBrandSelect(null)}
                  className={`pl-5 pr-2.5 py-1.5 text-xs flex items-center gap-2 rounded-sm ${
                    selectedBrand === null
                      ? "bg-[var(--color-primary)]/5 text-[var(--color-primary)] font-medium"
                      : "text-[var(--color-text-secondary)] hover:bg-black/3"
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full ${selectedBrand === null ? "bg-[var(--color-primary)]" : "bg-[var(--color-text-muted)]"}`} />
                  All Brands
                </button>

                {/* Zoning groups */}
                {BRAND_GROUPS.map((zone) => {
                  // Only show zonings that have at least one brand in DB
                  const hasAnyBrand = zone.groups.some(g => g.ids.some(id => brandMap[id]));
                  if (!hasAnyBrand) return null;

                  const isExpanded = expandedZoning === zone.zoning;

                  return (
                    <div key={zone.zoning}>
                      <button
                        onClick={() => toggleZoning(zone.zoning)}
                        className="w-full pl-5 pr-2.5 py-1.5 text-[10px] font-semibold tracking-wide text-[var(--color-text-muted)] flex items-center gap-1.5 hover:text-[var(--color-text-secondary)]"
                      >
                        <span className="text-[9px]">{isExpanded ? "▾" : "▸"}</span>
                        {zone.zoning}
                      </button>

                      {isExpanded && zone.groups.map((group) => {
                        const groupBrands = group.ids.filter(id => brandMap[id]);
                        if (groupBrands.length === 0) return null;
                        return (
                          <div key={group.region}>
                            <div className="pl-8 py-0.5 text-[9px] font-medium tracking-wider text-[var(--color-text-muted)] uppercase">
                              {group.region}
                            </div>
                            {groupBrands.map(id => (
                              <BrandButton key={id} brandId={id} />
                            ))}
                          </div>
                        );
                      })}
                    </div>
                  );
                })}

                {/* TBA brands */}
                {(() => {
                  const tbaBrands = TBA_BRAND_IDS.filter(id => brandMap[id]);
                  if (tbaBrands.length === 0) return null;
                  return (
                    <div>
                      <button
                        onClick={() => toggleZoning("__tba")}
                        className="w-full pl-5 pr-2.5 py-1.5 text-[10px] font-semibold tracking-wide text-[var(--color-text-muted)] flex items-center gap-1.5 hover:text-[var(--color-text-secondary)]"
                      >
                        <span className="text-[9px]">{expandedZoning === "__tba" ? "▾" : "▸"}</span>
                        TBA (수집 예정)
                      </button>
                      {expandedZoning === "__tba" && tbaBrands.map(id => {
                        const brand = brandMap[id];
                        return (
                          <div
                            key={id}
                            className="pl-10 pr-2.5 py-1 text-[11px] flex items-center gap-2 text-[var(--color-text-muted)]"
                          >
                            <span className="w-1.5 h-1.5 rounded-full shrink-0 bg-[var(--color-border)]" />
                            <span className="truncate">{brand.name}</span>
                          </div>
                        );
                      })}
                    </div>
                  );
                })()}

                {/* Ungrouped brands (not in any category) */}
                {ungroupedBrands.length > 0 && (
                  <div>
                    <button
                      onClick={() => toggleZoning("__other")}
                      className="w-full pl-5 pr-2.5 py-1.5 text-[10px] font-semibold tracking-wide text-[var(--color-text-muted)] flex items-center gap-1.5 hover:text-[var(--color-text-secondary)]"
                    >
                      <span className="text-[9px]">{expandedZoning === "__other" ? "▾" : "▸"}</span>
                      기타
                    </button>
                    {expandedZoning === "__other" && ungroupedBrands.map(brand => (
                      <BrandButton key={brand.id} brandId={brand.id} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </nav>
    </aside>
  );
}
