import { useQuery } from "@tanstack/react-query";
import { useState, useCallback, useRef, useEffect } from "react";
import axios from "axios";
import ForceGraph2D from "react-force-graph-2d";

const api = axios.create({ baseURL: "/api" });

function useMarketGraph() {
  return useQuery({
    queryKey: ["analysis", "graph"],
    queryFn: () => api.get("/analysis/graph").then(r => r.data),
  });
}

function useVlmGraph(season) {
  return useQuery({
    queryKey: ["analysis", "vlm-graph", season],
    queryFn: () => api.get("/analysis/vlm-graph", { params: season ? { season } : {} }).then(r => r.data),
  });
}

const MARKET_LEGEND = [
  { type: "brand", label: "Brand", color: "#A08B7A" },
  { type: "category", label: "Category", color: "#9E8DBE" },
  { type: "material", label: "Material", color: "#7B97AA" },
  { type: "color", label: "Color", color: "#90A0A8" },
];

const VLM_LEGEND = [
  { type: "designer", label: "Designer", color: "#8B7D6B" },
  { type: "color", label: "Color", color: "#90A0A8" },
  { type: "material", label: "Material", color: "#7B97AA" },
  { type: "silhouette", label: "Silhouette", color: "#9E8DBE" },
  { type: "texture", label: "Texture", color: "#A0887B" },
];

const VLM_SEASONS = [
  { value: "", label: "All Seasons" },
  { value: "spring-summer-2026", label: "SS26" },
  { value: "fall-winter-2026", label: "FW26" },
  { value: "spring-summer-2025", label: "SS25" },
  { value: "fall-winter-2025", label: "FW25" },
  { value: "spring-summer-2024", label: "SS24" },
  { value: "fall-winter-2024", label: "FW24" },
];

function LegendItem({ label, color }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
      <span className="text-[var(--color-text-secondary)]">{label}</span>
    </div>
  );
}

/* Shared graph canvas component */
function GraphCanvas({ data, isLoading, filter, setFilter, filterOptions, legend, selected, setSelected }) {
  const graphRef = useRef();
  const containerRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    if (!containerRef.current) return;
    const obs = new ResizeObserver(entries => {
      for (const entry of entries) {
        setDimensions({
          width: entry.contentRect.width,
          height: entry.contentRect.height,
        });
      }
    });
    obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  const centerNodeType = legend[0]?.type || "brand";

  const graphData = (() => {
    if (!data) return { nodes: [], links: [] };
    let nodes = data.nodes;
    let edges = data.edges;

    if (filter !== "all") {
      const typeNodes = new Set(
        nodes.filter(n => n.type === filter || n.type === centerNodeType).map(n => n.id)
      );
      nodes = nodes.filter(n => typeNodes.has(n.id));
      edges = edges.filter(e => typeNodes.has(e.source) && typeNodes.has(e.target));
    }

    return {
      nodes: nodes.map(n => ({ ...n, val: n.size })),
      links: edges.map(e => ({ source: e.source, target: e.target, value: e.weight })),
    };
  })();

  const handleNodeClick = useCallback((node) => {
    setSelected(node);
    if (graphRef.current) {
      graphRef.current.centerAt(node.x, node.y, 400);
      graphRef.current.zoom(2.5, 400);
    }
  }, [setSelected]);

  const paintNode = useCallback((node, ctx, globalScale) => {
    const size = node.size || 4;
    const isSelected = selected?.id === node.id;
    const r = size / 2;

    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
    ctx.fillStyle = node.color || "#999";
    ctx.fill();

    if (isSelected) {
      ctx.strokeStyle = "#E07070";
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    if (globalScale > 0.8 || node.type === centerNodeType) {
      const label = node.label || "";
      const fontSize = Math.max(12 / globalScale, 3);
      ctx.font = `${node.type === centerNodeType ? "600 " : ""}${fontSize}px sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = "#444";
      ctx.fillText(label, node.x, node.y + r + 1.5);
    }
  }, [selected, centerNodeType]);

  const connections = selected && data ? data.edges.filter(
    e => e.source === selected.id || e.target === selected.id
  ).map(e => {
    const otherId = e.source === selected.id ? e.target : e.source;
    const otherNode = data.nodes.find(n => n.id === otherId);
    return otherNode ? { ...otherNode, weight: e.weight } : null;
  }).filter(Boolean).sort((a, b) => b.weight - a.weight) : [];

  return (
    <div className="flex-1 flex overflow-hidden">
      <div className="flex-1 relative" ref={containerRef}>
        {/* Filters */}
        <div className="absolute top-4 left-4 z-10 flex gap-2">
          {filterOptions.map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 text-xs rounded-md border transition-colors ${
                filter === f
                  ? "bg-[var(--color-primary)] text-white border-[var(--color-primary)]"
                  : "bg-white border-[var(--color-border)] text-[var(--color-text-secondary)] hover:bg-gray-50"
              }`}
            >
              {f === "all" ? "All" : f.charAt(0).toUpperCase() + f.slice(1) + (f === "all" ? "" : "s")}
            </button>
          ))}
        </div>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 z-10 bg-white/90 border border-[var(--color-border)] rounded-md p-3 flex flex-col gap-1.5">
          {legend.map(l => <LegendItem key={l.type} {...l} />)}
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-full text-sm text-[var(--color-text-muted)]">
            Loading graph data...
          </div>
        ) : (
          <ForceGraph2D
            ref={graphRef}
            graphData={graphData}
            width={dimensions.width}
            height={dimensions.height}
            nodeCanvasObject={paintNode}
            nodePointerAreaPaint={(node, color, ctx) => {
              const r = (node.size || 6) / 2;
              ctx.beginPath();
              ctx.arc(node.x, node.y, r + 2, 0, 2 * Math.PI);
              ctx.fillStyle = color;
              ctx.fill();
            }}
            onNodeClick={handleNodeClick}
            linkWidth={link => Math.min(link.value || 1, 5) * 0.5}
            linkColor={() => "rgba(0,0,0,0.08)"}
            linkDirectionalParticles={0}
            cooldownTicks={100}
            d3AlphaDecay={0.02}
            d3VelocityDecay={0.3}
            backgroundColor="transparent"
          />
        )}
      </div>

      {/* Detail Panel */}
      <aside className="w-[260px] border-l border-[var(--color-border)] bg-white p-5 overflow-y-auto shrink-0">
        <h2 className="font-['Lora'] text-sm font-semibold mb-4">Node Detail</h2>
        {selected ? (
          <>
            <div className="mb-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-4 h-4 rounded-full" style={{ backgroundColor: selected.color }} />
                <span className="font-medium text-sm capitalize">{selected.label}</span>
              </div>
              <span className="text-[10px] font-semibold tracking-[1.5px] text-[var(--color-text-muted)] uppercase">{selected.type}</span>
            </div>

            <div className="mb-3">
              <span className="text-xs font-semibold text-[var(--color-text-muted)]">Connections ({connections.length})</span>
            </div>

            <div className="flex flex-col gap-1.5">
              {connections.slice(0, 20).map(conn => (
                <button
                  key={conn.id}
                  onClick={() => {
                    const node = graphData.nodes.find(n => n.id === conn.id);
                    if (node) handleNodeClick(node);
                  }}
                  className="text-left px-2.5 py-2 text-xs rounded-sm hover:bg-gray-50 flex items-center gap-2 border border-transparent hover:border-[var(--color-border)]"
                >
                  <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: conn.color }} />
                  <span className="truncate flex-1">{conn.label}</span>
                  <span className="text-[var(--color-text-muted)] shrink-0">{conn.type}</span>
                  <span className="text-[var(--color-text-muted)] shrink-0 w-6 text-right">{conn.weight}</span>
                </button>
              ))}
            </div>
          </>
        ) : (
          <p className="text-xs text-[var(--color-text-muted)]">Click a node to view connections.</p>
        )}
      </aside>
    </div>
  );
}

export default function GraphView() {
  const [mode, setMode] = useState("runway"); // "runway" | "market"
  const [vlmSeason, setVlmSeason] = useState("");
  const [marketFilter, setMarketFilter] = useState("all");
  const [vlmFilter, setVlmFilter] = useState("all");
  const [marketSelected, setMarketSelected] = useState(null);
  const [vlmSelected, setVlmSelected] = useState(null);

  const { data: marketData, isLoading: marketLoading } = useMarketGraph();
  const { data: vlmData, isLoading: vlmLoading } = useVlmGraph(vlmSeason || undefined);

  return (
    <main className="flex-1 flex flex-col overflow-hidden bg-[var(--color-bg)]">
      {/* Top Bar */}
      <div className="border-b border-[var(--color-border)] bg-white px-6 py-3 flex items-center gap-4 shrink-0">
        <h1 className="font-['Lora'] text-base font-semibold tracking-wide mr-2">Graph View</h1>

        {/* Mode Toggle */}
        <div className="flex bg-gray-100 rounded-md p-0.5">
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

        {/* VLM Season Filter */}
        {mode === "runway" && (
          <select
            value={vlmSeason}
            onChange={e => setVlmSeason(e.target.value)}
            className="text-xs border border-[var(--color-border)] rounded-md px-2.5 py-1.5 bg-white text-[var(--color-text-secondary)]"
          >
            {VLM_SEASONS.map(s => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        )}

        {/* Stats */}
        <div className="ml-auto text-[10px] text-[var(--color-text-muted)]">
          {mode === "runway" && vlmData && (
            <span>{vlmData.nodes?.length || 0} nodes &middot; {vlmData.edges?.length || 0} edges</span>
          )}
          {mode === "market" && marketData && (
            <span>{marketData.nodes?.length || 0} nodes &middot; {marketData.edges?.length || 0} edges</span>
          )}
        </div>
      </div>

      {/* Graph */}
      {mode === "runway" ? (
        <GraphCanvas
          data={vlmData}
          isLoading={vlmLoading}
          filter={vlmFilter}
          setFilter={setVlmFilter}
          filterOptions={["all", "color", "material", "silhouette", "texture"]}
          legend={VLM_LEGEND}
          selected={vlmSelected}
          setSelected={setVlmSelected}
        />
      ) : (
        <GraphCanvas
          data={marketData}
          isLoading={marketLoading}
          filter={marketFilter}
          setFilter={setMarketFilter}
          filterOptions={["all", "material", "color", "category"]}
          legend={MARKET_LEGEND}
          selected={marketSelected}
          setSelected={setMarketSelected}
        />
      )}
    </main>
  );
}
