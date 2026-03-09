import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter, Cell,
} from "recharts";

const api = axios.create({ baseURL: "/api" });

function useKpi() {
  return useQuery({ queryKey: ["analysis", "kpi"], queryFn: () => api.get("/analysis/kpi").then(r => r.data) });
}
function useColors() {
  return useQuery({ queryKey: ["analysis", "colors"], queryFn: () => api.get("/analysis/colors").then(r => r.data) });
}
function useMaterials() {
  return useQuery({ queryKey: ["analysis", "materials"], queryFn: () => api.get("/analysis/materials").then(r => r.data) });
}

const COLOR_MAP = {
  black: "#1a1a1a", white: "#bbb", gray: "#888", navy: "#1a237e",
  blue: "#2196F3", red: "#e53935", pink: "#EC407A", green: "#43A047",
  yellow: "#FDD835", beige: "#D4C5A9", brown: "#6D4C41", cream: "#f5f0d0",
  olive: "#808000", charcoal: "#36454F", mint: "#98FF98", ivory: "#f5f5e0",
  khaki: "#C3B091", orange: "#FF9800", purple: "#9C27B0",
};

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

function MaterialMatrix({ data }) {
  if (!data) return null;
  const { materials, matrix } = data;
  if (!materials?.length || !matrix?.length) return <p className="text-sm text-[var(--color-text-muted)]">No material data</p>;

  const maxVal = Math.max(...matrix.flatMap(row => materials.map(m => row[m] || 0)), 1);

  return (
    <div className="overflow-x-auto">
      <table className="text-xs w-full">
        <thead>
          <tr>
            <th className="text-left p-2 font-semibold text-[var(--color-text-muted)]">Brand</th>
            {materials.map(m => (
              <th key={m} className="p-2 font-medium text-[var(--color-text-secondary)] whitespace-nowrap text-center">{m}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map(row => (
            <tr key={row.brand} className="border-t border-[var(--color-border)]">
              <td className="p-2 font-medium">{row.brand}</td>
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

export default function TrendAnalysis() {
  const { data: kpi, isLoading: kpiLoading } = useKpi();
  const { data: colors } = useColors();
  const { data: materials } = useMaterials();

  return (
    <main className="flex-1 p-8 overflow-y-auto bg-[var(--color-bg)]">
      <div className="max-w-[1100px] mx-auto">
        <h1 className="font-['Lora'] text-xl font-semibold tracking-wide mb-1">Trend Analysis</h1>
        <p className="text-sm text-[var(--color-text-secondary)] mb-6">Cross-brand trend insights from crawled product data</p>

        {/* KPI Cards */}
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

        {/* Color Distribution */}
        <section className="bg-white border border-[var(--color-border)] rounded-md p-6 mb-6">
          <h2 className="font-['Lora'] text-base font-semibold mb-4">Color Distribution</h2>
          <ColorBubbles data={colors?.total} />
        </section>

        {/* Brand Color Bars */}
        {colors?.by_brand && (
          <section className="bg-white border border-[var(--color-border)] rounded-md p-6 mb-6">
            <h2 className="font-['Lora'] text-base font-semibold mb-4">Colors by Brand</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(colors.by_brand).map(([brand, brandColors]) => (
                <div key={brand}>
                  <h3 className="text-sm font-medium mb-2 capitalize">{brand}</h3>
                  <ResponsiveContainer width="100%" height={160}>
                    <BarChart data={brandColors.slice(0, 8)} layout="vertical">
                      <XAxis type="number" hide />
                      <YAxis type="category" dataKey="color" width={60} tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                        {brandColors.slice(0, 8).map((entry, i) => (
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

        {/* Material Matrix */}
        <section className="bg-white border border-[var(--color-border)] rounded-md p-6 mb-6">
          <h2 className="font-['Lora'] text-base font-semibold mb-4">Brand × Material Matrix</h2>
          <MaterialMatrix data={materials} />
        </section>
      </div>
    </main>
  );
}
