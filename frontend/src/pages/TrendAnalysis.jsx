import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell, PieChart, Pie, Legend,
} from "recharts";

const api = axios.create({ baseURL: "/api" });

/* ── Market hooks ── */
function useKpi() {
  return useQuery({ queryKey: ["analysis", "kpi"], queryFn: () => api.get("/analysis/kpi").then(r => r.data) });
}
function useColors() {
  return useQuery({ queryKey: ["analysis", "colors"], queryFn: () => api.get("/analysis/colors").then(r => r.data) });
}
function useMaterials() {
  return useQuery({ queryKey: ["analysis", "materials"], queryFn: () => api.get("/analysis/materials").then(r => r.data) });
}
function useCategories() {
  return useQuery({ queryKey: ["analysis", "categories"], queryFn: () => api.get("/analysis/categories").then(r => r.data) });
}

/* ── VLM hooks ── */
function useVlmKpi() {
  return useQuery({ queryKey: ["analysis", "vlm-kpi"], queryFn: () => api.get("/analysis/vlm-kpi").then(r => r.data) });
}
function useVlmColors() {
  return useQuery({ queryKey: ["analysis", "vlm-colors"], queryFn: () => api.get("/analysis/vlm-colors").then(r => r.data) });
}
function useVlmMaterials() {
  return useQuery({ queryKey: ["analysis", "vlm-materials"], queryFn: () => api.get("/analysis/vlm-materials").then(r => r.data) });
}
function useVlmSilhouettes() {
  return useQuery({ queryKey: ["analysis", "vlm-silhouettes"], queryFn: () => api.get("/analysis/vlm-silhouettes").then(r => r.data) });
}
function useVlmTextures() {
  return useQuery({ queryKey: ["analysis", "vlm-textures"], queryFn: () => api.get("/analysis/vlm-textures").then(r => r.data) });
}

const COLOR_MAP = {
  black: "#1a1a1a", white: "#bbb", gray: "#888", navy: "#1a237e",
  blue: "#2196F3", red: "#e53935", pink: "#EC407A", green: "#43A047",
  yellow: "#FDD835", beige: "#D4C5A9", brown: "#6D4C41", cream: "#f5f0d0",
  olive: "#808000", charcoal: "#36454F", mint: "#98FF98", ivory: "#f5f5e0",
  khaki: "#C3B091", orange: "#FF9800", purple: "#9C27B0", lavender: "#B39DDB",
  sand: "#C2B280", camel: "#C19A6B", teal: "#14B8A6", burgundy: "#800020",
  silver: "#C0C0C0", gold: "#D4A017",
};

const BRAND_COLORS = {
  alo: "#4ECDC4", newbalance: "#E74C3C", marithe: "#3498DB", asics: "#F39C12",
  coor: "#5B7553", blankroom: "#2C2C2C", youth: "#E67E22",
  lemaire: "#8D6E63", northface: "#D32F2F", descente: "#1565C0",
};

const DESIGNER_COLORS = [
  "#8B7D6B", "#7A8B6D", "#6B7A8B", "#8B6B7A", "#7D8B6B",
  "#6D7A8B", "#8B7A6B", "#6B8B7D", "#7A6B8B", "#8B6D7A",
];

const CAT_COLORS = ["#3498DB", "#E74C3C", "#2ECC71", "#F39C12", "#9B59B6", "#1ABC9C", "#E67E22", "#34495E", "#E91E63", "#00BCD4"];
const SIL_COLORS = ["#6366F1", "#8B5CF6", "#A78BFA", "#7C3AED", "#4F46E5", "#818CF8", "#C4B5FD", "#6D28D9", "#5B21B6", "#4338CA"];
const TEX_COLORS = ["#A0887B", "#8B7D6B", "#967860", "#B09478", "#7B97AA", "#6B8DAA", "#9E8DBE", "#7AAA88", "#C08080", "#C89870"];

function KpiCard({ label, value, sub }) {
  return (
    <div className="bg-white border border-[var(--color-border)] rounded-md p-5 flex flex-col gap-1">
      <span className="text-[10px] font-semibold tracking-[1.5px] text-[var(--color-text-muted)] uppercase">{label}</span>
      <span className="text-2xl font-['Lora'] font-semibold text-[var(--color-text)]">{value}</span>
      {sub && <span className="text-xs text-[var(--color-text-secondary)]">{sub}</span>}
    </div>
  );
}

function ColorBubbles({ data }) {
  if (!data?.length) return <p className="text-sm text-[var(--color-text-muted)]">No color data</p>;
  const maxCount = Math.max(...data.map(d => d.count));
  return (
    <div className="flex flex-wrap gap-3 items-end">
      {data.slice(0, 16).map((d) => {
        const size = 24 + (d.count / maxCount) * 48;
        return (
          <div key={d.color} className="flex flex-col items-center gap-1">
            <div
              style={{
                width: size, height: size, borderRadius: "50%",
                backgroundColor: COLOR_MAP[d.color] || "#78909C",
                border: d.color === "white" ? "1px solid #ccc" : "none",
              }}
              title={`${d.color}: ${d.count}`}
            />
            <span className="text-[10px] text-[var(--color-text-muted)]">{d.color}</span>
            <span className="text-[10px] font-medium">{d.count}</span>
          </div>
        );
      })}
    </div>
  );
}

function MaterialMatrix({ data, entityLabel = "Brand", entityKey = "brand" }) {
  if (!data) return null;
  const { materials, matrix } = data;
  if (!materials?.length || !matrix?.length) return <p className="text-sm text-[var(--color-text-muted)]">No material data</p>;

  const maxVal = Math.max(...matrix.flatMap(row => materials.map(m => row[m] || 0)), 1);

  return (
    <div className="overflow-x-auto">
      <table className="text-xs w-full">
        <thead>
          <tr>
            <th className="text-left p-2 font-semibold text-[var(--color-text-muted)]">{entityLabel}</th>
            {materials.map(m => (
              <th key={m} className="p-2 font-medium text-[var(--color-text-secondary)] whitespace-nowrap text-center">{m}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map(row => (
            <tr key={row[entityKey]} className="border-t border-[var(--color-border)]">
              <td className="p-2 font-medium capitalize">{row[entityKey]}</td>
              {materials.map(m => {
                const val = row[m] || 0;
                const intensity = val / maxVal;
                return (
                  <td key={m} className="p-2 text-center" style={{
                    backgroundColor: val > 0 ? `rgba(37, 99, 235, ${0.1 + intensity * 0.6})` : "transparent",
                    color: intensity > 0.5 ? "white" : "inherit",
                  }}>
                    {val || ""}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function HorizontalBarChart({ data, dataKey, nameKey, colors, height }) {
  if (!data?.length) return <p className="text-sm text-[var(--color-text-muted)]">No data</p>;
  const h = height || Math.max(200, data.length * 32);
  return (
    <ResponsiveContainer width="100%" height={h}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20 }}>
        <XAxis type="number" tick={{ fontSize: 11 }} />
        <YAxis type="category" dataKey={nameKey} width={90} tick={{ fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey={dataKey} radius={[0, 4, 4, 0]}>
          {data.map((entry, i) => (
            <Cell key={i} fill={typeof colors === "function" ? colors(entry, i) : (Array.isArray(colors) ? colors[i % colors.length] : "#78909C")} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function CategoryChart({ data }) {
  if (!data || Object.keys(data).length === 0) return <p className="text-sm text-[var(--color-text-muted)]">No category data</p>;
  const allCategories = new Set();
  Object.values(data).forEach(cats => Object.keys(cats).forEach(c => allCategories.add(c)));
  const categories = [...allCategories].sort();
  const chartData = Object.entries(data).map(([brand, cats]) => {
    const row = { brand };
    categories.forEach(c => { row[c] = cats[c] || 0; });
    return row;
  }).sort((a, b) => {
    const totalA = categories.reduce((s, c) => s + (a[c] || 0), 0);
    const totalB = categories.reduce((s, c) => s + (b[c] || 0), 0);
    return totalB - totalA;
  });

  return (
    <ResponsiveContainer width="100%" height={Math.max(300, chartData.length * 36)}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 10, right: 20 }}>
        <XAxis type="number" tick={{ fontSize: 11 }} />
        <YAxis type="category" dataKey="brand" width={80} tick={{ fontSize: 11 }} />
        <Tooltip />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        {categories.map((cat, i) => (
          <Bar key={cat} dataKey={cat} stackId="a" fill={CAT_COLORS[i % CAT_COLORS.length]} radius={i === categories.length - 1 ? [0, 4, 4, 0] : [0, 0, 0, 0]} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

function BrandProductCount({ data }) {
  if (!data || Object.keys(data).length === 0) return null;
  const chartData = Object.entries(data).map(([brand, cats]) => ({
    brand,
    total: Object.values(cats).reduce((s, v) => s + v, 0),
  })).sort((a, b) => b.total - a.total);

  return (
    <HorizontalBarChart
      data={chartData}
      dataKey="total"
      nameKey="brand"
      colors={(entry) => BRAND_COLORS[entry.brand] || "#78909C"}
    />
  );
}

/* ── Designer-level color breakdown (VLM) ── */
function DesignerColorGrid({ byDesigner }) {
  if (!byDesigner || Object.keys(byDesigner).length === 0) return null;
  const sorted = Object.entries(byDesigner).sort((a, b) => {
    const totalA = a[1].reduce((s, v) => s + v.count, 0);
    const totalB = b[1].reduce((s, v) => s + v.count, 0);
    return totalB - totalA;
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {sorted.slice(0, 12).map(([designer, designerColors], di) => (
        <div key={designer}>
          <h3 className="text-sm font-medium mb-2 capitalize flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: DESIGNER_COLORS[di % DESIGNER_COLORS.length] }} />
            {designer}
          </h3>
          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={designerColors.slice(0, 6)} layout="vertical">
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="color" width={55} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {designerColors.slice(0, 6).map((entry, i) => (
                  <Cell key={i} fill={COLOR_MAP[entry.color] || "#78909C"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ))}
    </div>
  );
}

/* ══════════════════ Market Analysis Panel ══════════════════ */
function MarketAnalysis() {
  const { data: kpi, isLoading: kpiLoading } = useKpi();
  const { data: colors } = useColors();
  const { data: materials } = useMaterials();
  const { data: categories } = useCategories();

  return (
    <>
      {kpiLoading ? (
        <div className="text-sm text-[var(--color-text-muted)]">Loading...</div>
      ) : (
        <div className="grid grid-cols-4 gap-4 mb-8">
          <KpiCard label="Total Products" value={kpi?.total_products ?? 0} />
          <KpiCard label="Top Color" value={kpi?.top_color?.name ?? "N/A"} sub={`${kpi?.top_color?.count ?? 0} products`} />
          <KpiCard label="Trending Fit" value={kpi?.trending_fit?.name ?? "N/A"} sub={`${kpi?.trending_fit?.count ?? 0} products`} />
          <KpiCard label="Top Material" value={kpi?.top_material?.name ?? "N/A"} sub={`${kpi?.top_material?.count ?? 0} products`} />
        </div>
      )}

      <section className="bg-white border border-[var(--color-border)] rounded-md p-6 mb-6">
        <h2 className="font-['Lora'] text-base font-semibold mb-4">Color Distribution</h2>
        <ColorBubbles data={colors?.total} />
      </section>

      {colors?.by_brand && (
        <section className="bg-white border border-[var(--color-border)] rounded-md p-6 mb-6">
          <h2 className="font-['Lora'] text-base font-semibold mb-4">Colors by Brand</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(colors.by_brand).map(([brand, brandColors]) => (
              <div key={brand}>
                <h3 className="text-sm font-medium mb-2 capitalize flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: BRAND_COLORS[brand] || "#78909C" }} />
                  {brand}
                </h3>
                <ResponsiveContainer width="100%" height={140}>
                  <BarChart data={brandColors.slice(0, 6)} layout="vertical">
                    <XAxis type="number" hide />
                    <YAxis type="category" dataKey="color" width={55} tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                      {brandColors.slice(0, 6).map((entry, i) => (
                        <Cell key={i} fill={COLOR_MAP[entry.color] || "#78909C"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <section className="bg-white border border-[var(--color-border)] rounded-md p-6">
          <h2 className="font-['Lora'] text-base font-semibold mb-4">Products by Brand</h2>
          <BrandProductCount data={categories} />
        </section>
        <section className="bg-white border border-[var(--color-border)] rounded-md p-6">
          <h2 className="font-['Lora'] text-base font-semibold mb-4">Category Distribution</h2>
          <CategoryChart data={categories} />
        </section>
      </div>

      <section className="bg-white border border-[var(--color-border)] rounded-md p-6 mb-6">
        <h2 className="font-['Lora'] text-base font-semibold mb-4">Brand × Material Matrix</h2>
        <MaterialMatrix data={materials} entityLabel="Brand" entityKey="brand" />
      </section>
    </>
  );
}

/* ══════════════════ Runway VLM Analysis Panel ══════════════════ */
function RunwayAnalysis() {
  const { data: kpi, isLoading: kpiLoading } = useVlmKpi();
  const { data: colors } = useVlmColors();
  const { data: materials } = useVlmMaterials();
  const { data: silhouettes } = useVlmSilhouettes();
  const { data: textures } = useVlmTextures();

  return (
    <>
      {kpiLoading ? (
        <div className="text-sm text-[var(--color-text-muted)]">Loading...</div>
      ) : (
        <div className="grid grid-cols-4 gap-4 mb-8">
          <KpiCard label="Labeled Looks" value={kpi?.total_looks ?? 0} />
          <KpiCard label="Top Color" value={kpi?.top_color?.name ?? "N/A"} sub={`${kpi?.top_color?.count ?? 0} looks`} />
          <KpiCard label="Top Silhouette" value={kpi?.top_silhouette?.name ?? "N/A"} sub={`${kpi?.top_silhouette?.count ?? 0} looks`} />
          <KpiCard label="Top Material" value={kpi?.top_material?.name ?? "N/A"} sub={`${kpi?.top_material?.count ?? 0} looks`} />
        </div>
      )}

      {/* Color Distribution */}
      <section className="bg-white border border-[var(--color-border)] rounded-md p-6 mb-6">
        <h2 className="font-['Lora'] text-base font-semibold mb-4">Runway Color Distribution</h2>
        <ColorBubbles data={colors?.total} />
      </section>

      {/* Colors by Designer */}
      {colors?.by_designer && (
        <section className="bg-white border border-[var(--color-border)] rounded-md p-6 mb-6">
          <h2 className="font-['Lora'] text-base font-semibold mb-4">Colors by Designer</h2>
          <DesignerColorGrid byDesigner={colors.by_designer} />
        </section>
      )}

      {/* Silhouette + Texture side-by-side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <section className="bg-white border border-[var(--color-border)] rounded-md p-6">
          <h2 className="font-['Lora'] text-base font-semibold mb-4">Silhouette Distribution</h2>
          <HorizontalBarChart
            data={silhouettes?.total}
            dataKey="count"
            nameKey="silhouette"
            colors={SIL_COLORS}
          />
        </section>
        <section className="bg-white border border-[var(--color-border)] rounded-md p-6">
          <h2 className="font-['Lora'] text-base font-semibold mb-4">Texture Distribution</h2>
          <HorizontalBarChart
            data={textures?.total}
            dataKey="count"
            nameKey="texture"
            colors={TEX_COLORS}
          />
        </section>
      </div>

      {/* Designer × Material Matrix */}
      <section className="bg-white border border-[var(--color-border)] rounded-md p-6 mb-6">
        <h2 className="font-['Lora'] text-base font-semibold mb-4">Designer × Material Matrix</h2>
        <MaterialMatrix data={materials} entityLabel="Designer" entityKey="designer" />
      </section>
    </>
  );
}

/* ══════════════════ Main Component ══════════════════ */
export default function TrendAnalysis() {
  const [mode, setMode] = useState("runway"); // "runway" | "market"

  return (
    <main className="flex-1 flex flex-col overflow-hidden bg-[var(--color-bg)]">
      {/* Sticky Header + Toggle */}
      <div className="shrink-0 bg-[var(--color-bg)] border-b border-[var(--color-border)] px-8 pt-6 pb-4">
        <div className="max-w-[1100px] mx-auto flex items-center gap-4">
          <div>
            <h1 className="font-['Lora'] text-xl font-semibold tracking-wide mb-1">Trend Analysis</h1>
            <p className="text-sm text-[var(--color-text-secondary)]">
              {mode === "runway"
                ? "Runway VLM label analysis — colors, silhouettes, materials, textures"
                : "Cross-brand trend insights from crawled product data"}
            </p>
          </div>
          <div className="ml-auto flex bg-gray-100 rounded-md p-0.5">
            <button
              onClick={() => setMode("runway")}
              className={`px-4 py-1.5 text-xs rounded-md transition-colors ${
                mode === "runway"
                  ? "bg-white text-[var(--color-primary)] font-medium shadow-sm"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"
              }`}
            >
              Runway (VLM)
            </button>
            <button
              onClick={() => setMode("market")}
              className={`px-4 py-1.5 text-xs rounded-md transition-colors ${
                mode === "market"
                  ? "bg-white text-[var(--color-primary)] font-medium shadow-sm"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"
              }`}
            >
              Market Brand
            </button>
          </div>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        <div className="max-w-[1100px] mx-auto">
          {mode === "runway" ? <RunwayAnalysis /> : <MarketAnalysis />}
        </div>
      </div>
    </main>
  );
}
