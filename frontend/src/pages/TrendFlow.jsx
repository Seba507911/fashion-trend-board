import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const api = axios.create({ baseURL: "/api" });

function useRunwaySignals() {
  return useQuery({ queryKey: ["trendflow", "runway"], queryFn: () => api.get("/trendflow/runway-signals").then(r => r.data) });
}
function useMarketValidation() {
  return useQuery({ queryKey: ["trendflow", "market"], queryFn: () => api.get("/trendflow/market-validation").then(r => r.data) });
}
function useCelebMock() {
  return useQuery({ queryKey: ["trendflow", "celeb"], queryFn: () => api.get("/trendflow/celeb-mock").then(r => r.data) });
}
function useExpertMock() {
  return useQuery({ queryKey: ["trendflow", "expert"], queryFn: () => api.get("/trendflow/expert-mock").then(r => r.data) });
}
function useForecastMock() {
  return useQuery({ queryKey: ["trendflow", "forecast"], queryFn: () => api.get("/trendflow/forecast-mock").then(r => r.data) });
}
function useKeywords() {
  return useQuery({ queryKey: ["trendflow", "keywords"], queryFn: () => api.get("/trendflow/keywords").then(r => r.data) });
}

const STAGE_COLORS = ["#E74C3C", "#F39C12", "#9B59B6", "#3498DB", "#2ECC71"];
const BRAND_COLORS = {
  alo: "#4ECDC4", newbalance: "#E74C3C", marithe: "#3498DB", asics: "#F39C12",
  coor: "#5B7553", blankroom: "#2C2C2C", youth: "#E67E22",
  lemaire: "#8D6E63", northface: "#D32F2F", descente: "#1565C0",
};
const GROUP_COLORS = { color: "#E74C3C", material: "#3498DB", silhouette: "#9B59B6", category: "#2ECC71", style: "#F39C12" };

/* ── Pipeline Step Header ── */
function StepHeader({ number, title, subtitle, color }) {
  return (
    <div className="flex items-center gap-3 mb-4">
      <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold shrink-0" style={{ backgroundColor: color }}>
        {number}
      </div>
      <div>
        <h2 className="font-['Lora'] text-sm font-semibold tracking-wide">{title}</h2>
        <p className="text-[10px] text-[var(--color-text-muted)]">{subtitle}</p>
      </div>
    </div>
  );
}

/* ── Flow Arrow ── */
function FlowArrow() {
  return (
    <div className="flex items-center justify-center py-2">
      <div className="flex items-center gap-1 text-[var(--color-text-muted)]">
        <div className="w-8 border-t border-dashed border-[var(--color-border)]" />
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 5v14M19 12l-7 7-7-7" />
        </svg>
        <div className="w-8 border-t border-dashed border-[var(--color-border)]" />
      </div>
    </div>
  );
}

/* ── Keyword Tag ── */
function KeywordTag({ label, group, active, onClick, size = "sm" }) {
  const base = size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-1 text-xs";
  return (
    <button
      onClick={onClick}
      className={`${base} rounded-full border transition-all ${
        active
          ? "border-[var(--color-primary)] bg-[var(--color-primary)] text-white"
          : "border-[var(--color-border)] bg-white text-[var(--color-text-secondary)] hover:border-gray-400"
      }`}
    >
      <span className="inline-block w-1.5 h-1.5 rounded-full mr-1" style={{ backgroundColor: GROUP_COLORS[group] || "#999" }} />
      {label}
    </button>
  );
}

/* ── Stage 1: Runway Signals ── */
function RunwaySignals({ data, activeKeyword }) {
  if (!data) return <Skeleton />;

  const filtered = activeKeyword
    ? data.top_signals.filter(s => s.keyword.includes(activeKeyword))
    : data.top_signals.slice(0, 12);

  return (
    <div className="bg-white border border-[var(--color-border)] rounded-md p-5">
      <StepHeader number={1} title="Runway Signal" subtitle={`${data.total_looks} looks from ${Object.keys(data.designer_focus).length} designers`} color={STAGE_COLORS[0]} />
      <div className="grid grid-cols-2 gap-4">
        <div>
          <span className="text-[10px] font-semibold tracking-widest text-[var(--color-text-muted)] uppercase">Top Keywords</span>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={filtered.slice(0, 10)} layout="vertical" margin={{ left: 5, right: 10 }}>
              <XAxis type="number" tick={{ fontSize: 10 }} />
              <YAxis type="category" dataKey="keyword" width={70} tick={{ fontSize: 10 }} />
              <Tooltip formatter={(v) => [`${v} looks`]} />
              <Bar dataKey="count" radius={[0, 3, 3, 0]}>
                {filtered.slice(0, 10).map((_, i) => (
                  <Cell key={i} fill={`${STAGE_COLORS[0]}${i < 3 ? "" : "80"}`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div>
          <span className="text-[10px] font-semibold tracking-widest text-[var(--color-text-muted)] uppercase">Designer Focus</span>
          <div className="mt-2 space-y-2 max-h-[220px] overflow-y-auto pr-1">
            {Object.entries(data.designer_focus).slice(0, 8).map(([designer, tags]) => (
              <div key={designer} className="flex items-start gap-2">
                <span className="text-[11px] font-medium w-20 shrink-0 truncate">{designer}</span>
                <div className="flex flex-wrap gap-1">
                  {tags.slice(0, 3).map(t => (
                    <span key={t.keyword} className="text-[9px] px-1.5 py-0.5 bg-red-50 text-red-700 rounded">
                      {t.keyword} ({t.count})
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Stage 2: Expert Report ── */
function ExpertReport({ data }) {
  if (!data) return <Skeleton />;

  const allPredictions = data.reports.flatMap(r => r.predictions.map(p => ({ ...p, source: r.source })));
  const matched = allPredictions.filter(p => p.runway_match).length;
  const total = allPredictions.length;

  return (
    <div className="bg-white border border-[var(--color-border)] rounded-md p-5">
      <StepHeader number={2} title="Expert Report" subtitle={`${data.reports.length} reports analyzed`} color={STAGE_COLORS[1]} />
      <div className="flex items-center gap-6 mb-4">
        <div className="text-center">
          <div className="text-2xl font-['Lora'] font-bold text-[var(--color-primary)]">{Math.round(matched / total * 100)}%</div>
          <div className="text-[10px] text-[var(--color-text-muted)]">Runway Match Rate</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-['Lora'] font-bold">{matched}/{total}</div>
          <div className="text-[10px] text-[var(--color-text-muted)]">Predictions Verified</div>
        </div>
      </div>
      <div className="space-y-3">
        {data.reports.map(report => (
          <div key={report.id} className="border border-[var(--color-border)] rounded p-3">
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="text-[10px] font-bold tracking-widest text-amber-600 uppercase">{report.source}</span>
                <span className="text-[10px] text-[var(--color-text-muted)] ml-2">{report.date}</span>
              </div>
              <span className="text-[10px] px-2 py-0.5 bg-amber-50 text-amber-700 rounded-full">
                {report.predictions.filter(p => p.runway_match).length}/{report.predictions.length} matched
              </span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {report.predictions.map(pred => (
                <span
                  key={pred.keyword}
                  className={`text-[10px] px-2 py-0.5 rounded-full border ${
                    pred.runway_match
                      ? "bg-green-50 text-green-700 border-green-200"
                      : "bg-gray-50 text-gray-500 border-gray-200 line-through"
                  }`}
                >
                  {pred.keyword}
                  {pred.confidence === "high" && " ★"}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3 border-2 border-dashed border-[var(--color-border)] rounded-md p-4 text-center text-[var(--color-text-muted)]">
        <svg className="mx-auto mb-1 w-6 h-6 opacity-40" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 16v-4m0 0V8m0 4h4m-4 0H8m13 4v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2m14-10V4a2 2 0 00-2-2H9a2 2 0 00-2 2v4" />
        </svg>
        <p className="text-xs">Drop PDF report here to analyze</p>
        <p className="text-[10px] mt-0.5">(WGSN, Pantone, EDITED 등)</p>
      </div>
    </div>
  );
}

/* ── Stage 3: Celebrity & Influencer ── */
function CelebInfluencer({ data, activeKeyword }) {
  const [activeTab, setActiveTab] = useState("global_celeb");

  if (!data) return <Skeleton />;

  const activeGroup = data.groups.find(g => g.id === activeTab);
  const people = activeGroup?.people || [];

  // 키워드 적중률 히트맵 데이터
  const allKeywords = [...new Set(data.groups.flatMap(g => g.people.flatMap(p => p.tags)))];

  return (
    <div className="bg-white border border-[var(--color-border)] rounded-md p-5">
      <StepHeader number={3} title="Celebrity & Influencer" subtitle="Trend adoption monitoring" color={STAGE_COLORS[2]} />

      <div className="flex gap-1 mb-4">
        {data.groups.map(g => (
          <button
            key={g.id}
            onClick={() => setActiveTab(g.id)}
            className={`px-2.5 py-1.5 text-[10px] rounded-md border transition-colors ${
              activeTab === g.id
                ? "bg-purple-600 text-white border-purple-600"
                : "border-[var(--color-border)] text-[var(--color-text-secondary)] hover:bg-gray-50"
            }`}
          >
            {g.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        {people.map(person => {
          const highlighted = activeKeyword ? person.tags.includes(activeKeyword) : false;
          return (
            <div
              key={person.name}
              className={`border rounded-md p-3 transition-all ${highlighted ? "border-purple-400 bg-purple-50/50" : "border-[var(--color-border)]"}`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium">{person.name}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                  person.trend_match >= 85 ? "bg-green-100 text-green-700" :
                  person.trend_match >= 70 ? "bg-amber-100 text-amber-700" :
                  "bg-gray-100 text-gray-600"
                }`}>
                  {person.trend_match}% match
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {person.tags.map(tag => (
                  <span
                    key={tag}
                    className={`text-[9px] px-1.5 py-0.5 rounded ${
                      tag === activeKeyword ? "bg-purple-200 text-purple-800 font-medium" : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {tag}
                  </span>
                ))}
              </div>
              <div className="text-[10px] text-[var(--color-text-muted)] mt-1.5">{person.looks} looks tracked</div>
            </div>
          );
        })}
      </div>

      {/* Keyword Heatmap */}
      <div className="overflow-x-auto">
        <span className="text-[10px] font-semibold tracking-widest text-[var(--color-text-muted)] uppercase">Keyword × Person Matrix</span>
        <table className="text-[9px] w-full mt-1">
          <thead>
            <tr>
              <th className="text-left p-1 font-medium">Person</th>
              {allKeywords.slice(0, 8).map(k => (
                <th key={k} className="p-1 font-medium text-center">{k}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.groups.flatMap(g => g.people).map(p => (
              <tr key={p.name} className="border-t border-[var(--color-border)]">
                <td className="p-1 font-medium">{p.name}</td>
                {allKeywords.slice(0, 8).map(k => (
                  <td key={k} className="p-1 text-center">
                    {p.tags.includes(k) ? (
                      <span className="inline-block w-3 h-3 rounded-sm bg-purple-500" />
                    ) : (
                      <span className="inline-block w-3 h-3 rounded-sm bg-gray-100" />
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ── Stage 4: Market Validation ── */
function MarketValidation({ data, activeKeyword }) {
  if (!data) return <Skeleton />;

  const kwData = activeKeyword && data.keyword_matches[activeKeyword]
    ? [data.keyword_matches[activeKeyword]]
    : Object.values(data.keyword_matches).sort((a, b) => b.matched_products - a.matched_products).slice(0, 8);

  return (
    <div className="bg-white border border-[var(--color-border)] rounded-md p-5">
      <StepHeader number={4} title="Market Validation" subtitle={`${data.total_products} products across all brands`} color={STAGE_COLORS[3]} />

      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center border border-[var(--color-border)] rounded-md p-3">
          <div className="text-xl font-['Lora'] font-bold text-blue-600">{data.total_products}</div>
          <div className="text-[10px] text-[var(--color-text-muted)]">Total Products</div>
        </div>
        <div className="text-center border border-[var(--color-border)] rounded-md p-3">
          <div className="text-xl font-['Lora'] font-bold text-blue-600">{data.top_colors?.[0]?.color || "—"}</div>
          <div className="text-[10px] text-[var(--color-text-muted)]">Top Market Color</div>
        </div>
        <div className="text-center border border-[var(--color-border)] rounded-md p-3">
          <div className="text-xl font-['Lora'] font-bold text-blue-600">{data.categories?.[0]?.category || "—"}</div>
          <div className="text-[10px] text-[var(--color-text-muted)]">Top Category</div>
        </div>
      </div>

      <span className="text-[10px] font-semibold tracking-widest text-[var(--color-text-muted)] uppercase">Keyword Match in Market</span>
      <div className="space-y-2 mt-2">
        {kwData.map(kw => (
          <div key={kw.keyword} className="border border-[var(--color-border)] rounded p-3">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-medium">{kw.keyword}</span>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-[var(--color-text-muted)]">{kw.matched_products} products</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                  kw.match_rate >= 10 ? "bg-blue-100 text-blue-700" :
                  kw.match_rate >= 3 ? "bg-amber-100 text-amber-700" :
                  "bg-gray-100 text-gray-600"
                }`}>
                  {kw.match_rate}%
                </span>
              </div>
            </div>
            {/* Progress bar */}
            <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden mb-1.5">
              <div
                className="h-full rounded-full bg-blue-500 transition-all"
                style={{ width: `${Math.min(kw.match_rate * 3, 100)}%` }}
              />
            </div>
            {kw.by_brand.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {kw.by_brand.slice(0, 5).map(b => (
                  <span key={b.brand} className="text-[9px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-700">
                    {b.brand}: {b.count}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Mock signal indicators */}
      <div className="mt-4 grid grid-cols-3 gap-2">
        <MockSignal label="SNS Mentions" value="12.4K" trend="+32%" positive />
        <MockSignal label="Naver Search" value="8.7K" trend="+18%" positive />
        <MockSignal label="Sold-out Rate" value="23%" trend="+5%" positive />
      </div>
    </div>
  );
}

function MockSignal({ label, value, trend, positive }) {
  return (
    <div className="border border-dashed border-[var(--color-border)] rounded p-2.5 text-center">
      <div className="text-sm font-bold">{value}</div>
      <div className={`text-[10px] font-medium ${positive ? "text-green-600" : "text-red-500"}`}>{trend}</div>
      <div className="text-[9px] text-[var(--color-text-muted)] mt-0.5">{label}</div>
      <div className="text-[8px] text-[var(--color-text-muted)] italic">mock</div>
    </div>
  );
}

/* ── Stage 5: Next Runway Forecast ── */
function ForecastPanel({ data }) {
  if (!data) return <Skeleton />;

  const sections = [
    { key: "expanding", label: "Expanding", icon: "↑", color: "green", items: data.expanding },
    { key: "shrinking", label: "Shrinking", icon: "↓", color: "red", items: data.shrinking },
    { key: "morphing", label: "Morphing", icon: "↗", color: "amber", items: data.morphing },
  ];

  return (
    <div className="bg-white border border-[var(--color-border)] rounded-md p-5">
      <StepHeader number={5} title="Next Runway Forecast" subtitle="Trend direction prediction for SS27" color={STAGE_COLORS[4]} />
      <div className="grid grid-cols-3 gap-3">
        {sections.map(sec => (
          <div key={sec.key}>
            <div className={`flex items-center gap-1.5 mb-2 text-${sec.color}-600`}>
              <span className="text-lg font-bold">{sec.icon}</span>
              <span className="text-xs font-semibold">{sec.label}</span>
            </div>
            <div className="space-y-2">
              {sec.items.map(item => (
                <div key={item.keyword} className={`border-l-2 border-${sec.color}-400 pl-2.5 py-1`}>
                  <div className="text-xs font-medium">{item.keyword}</div>
                  <div className="text-[9px] text-[var(--color-text-muted)] mt-0.5">{item.signal}</div>
                  <div className="flex items-center gap-1 mt-1">
                    <div className="w-12 h-1 bg-gray-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full bg-${sec.color}-500`} style={{ width: `${item.confidence}%` }} />
                    </div>
                    <span className="text-[9px] text-[var(--color-text-muted)]">{item.confidence}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Skeleton ── */
function Skeleton() {
  return (
    <div className="bg-white border border-[var(--color-border)] rounded-md p-5 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-1/3 mb-3" />
      <div className="h-32 bg-gray-100 rounded" />
    </div>
  );
}

/* ── Main Page ── */
export default function TrendFlow() {
  const [activeKeyword, setActiveKeyword] = useState(null);
  const { data: keywords } = useKeywords();
  const { data: runway } = useRunwaySignals();
  const { data: market } = useMarketValidation();
  const { data: celeb } = useCelebMock();
  const { data: expert } = useExpertMock();
  const { data: forecast } = useForecastMock();

  return (
    <main className="flex-1 overflow-y-auto bg-[var(--color-bg)]">
      {/* Sticky Keyword Bar */}
      <div className="sticky top-0 z-20 bg-[var(--color-bg)]/95 backdrop-blur border-b border-[var(--color-border)] px-8 py-3">
        <div className="max-w-[1100px] mx-auto">
          <div className="flex items-center gap-3">
            <span className="text-[10px] font-semibold tracking-widest text-[var(--color-text-muted)] uppercase shrink-0">
              Tracking
            </span>
            <div className="flex flex-wrap gap-1.5">
              <button
                onClick={() => setActiveKeyword(null)}
                className={`px-2 py-0.5 text-[10px] rounded-full border transition-colors ${
                  !activeKeyword ? "bg-gray-800 text-white border-gray-800" : "border-[var(--color-border)] text-[var(--color-text-muted)]"
                }`}
              >
                All
              </button>
              {(keywords || []).map(kw => (
                <KeywordTag
                  key={kw.id}
                  label={kw.label}
                  group={kw.group}
                  active={activeKeyword === kw.id}
                  onClick={() => setActiveKeyword(activeKeyword === kw.id ? null : kw.id)}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Pipeline Content */}
      <div className="max-w-[1100px] mx-auto px-8 py-6">
        <h1 className="font-['Lora'] text-xl font-semibold tracking-wide mb-1">Trend Flow</h1>
        <p className="text-sm text-[var(--color-text-secondary)] mb-6">
          Runway → Expert → Celebrity → Market — end-to-end trend propagation tracker
        </p>

        {/* Pipeline visualization */}
        <div className="flex items-center justify-between mb-6 px-4">
          {["Runway", "Expert", "Celeb", "Market", "Forecast"].map((label, i) => (
            <div key={label} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold shadow-sm"
                  style={{ backgroundColor: STAGE_COLORS[i] }}
                >
                  {i + 1}
                </div>
                <span className="text-[10px] font-medium mt-1 text-[var(--color-text-secondary)]">{label}</span>
              </div>
              {i < 4 && (
                <div className="w-16 h-0.5 mx-1" style={{
                  background: `linear-gradient(to right, ${STAGE_COLORS[i]}, ${STAGE_COLORS[i + 1]})`,
                }} />
              )}
            </div>
          ))}
        </div>

        {/* Stages */}
        <RunwaySignals data={runway} activeKeyword={activeKeyword} />
        <FlowArrow />
        <ExpertReport data={expert} />
        <FlowArrow />
        <CelebInfluencer data={celeb} activeKeyword={activeKeyword} />
        <FlowArrow />
        <MarketValidation data={market} activeKeyword={activeKeyword} />
        <FlowArrow />
        <ForecastPanel data={forecast} />

        <div className="h-8" />
      </div>
    </main>
  );
}
