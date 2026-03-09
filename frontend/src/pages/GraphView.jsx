import { useQuery } from "@tanstack/react-query";
import { useState, useCallback, useRef, useEffect } from "react";
import axios from "axios";
import ForceGraph2D from "react-force-graph-2d";

const api = axios.create({ baseURL: "/api" });

function useGraphData() {
  return useQuery({
    queryKey: ["analysis", "graph"],
    queryFn: () => api.get("/analysis/graph").then(r => r.data),
  });
}

const TYPE_SHAPES = {
  brand: "circle",
  material: "diamond",
  color: "circle",
  category: "square",
};

const LEGEND = [
  { type: "brand", label: "Brand", color: "#4ECDC4", shape: "circle" },
  { type: "category", label: "Category", color: "#8E44AD", shape: "square" },
  { type: "material", label: "Material", color: "#2C3E50", shape: "diamond" },
  { type: "color", label: "Color", color: "#78909C", shape: "circle" },
];

function LegendItem({ label, color, shape }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      {shape === "square" ? (
        <div className="w-3 h-3 rounded-[2px]" style={{ backgroundColor: color }} />
      ) : shape === "diamond" ? (
        <div className="w-3 h-3 rotate-45 rounded-[1px]" style={{ backgroundColor: color }} />
      ) : (
        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
      )}
      <span className="text-[var(--color-text-secondary)]">{label}</span>
    </div>
  );
}

export default function GraphView() {
  const { data, isLoading } = useGraphData();
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("all");
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

  const graphData = (() => {
    if (!data) return { nodes: [], links: [] };
    let nodes = data.nodes;
    let edges = data.edges;

    if (filter !== "all") {
      const typeNodes = new Set(nodes.filter(n => n.type === filter || n.type === "brand").map(n => n.id));
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
  }, []);

  const paintNode = useCallback((node, ctx, globalScale) => {
    const size = node.size || 6;
    const isSelected = selected?.id === node.id;
    const r = size / 2;

    ctx.beginPath();
    if (node.type === "square" || node.type === "category") {
      ctx.rect(node.x - r, node.y - r, size, size);
    } else if (node.type === "material") {
      ctx.moveTo(node.x, node.y - r);
      ctx.lineTo(node.x + r, node.y);
      ctx.lineTo(node.x, node.y + r);
      ctx.lineTo(node.x - r, node.y);
      ctx.closePath();
    } else {
      ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
    }

    ctx.fillStyle = node.color || "#999";
    ctx.fill();

    if (isSelected) {
      ctx.strokeStyle = "#FF6B6B";
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Label
    if (globalScale > 1.2 || node.type === "brand") {
      const label = node.label || "";
      const fontSize = Math.max(10 / globalScale, 2);
      ctx.font = `${node.type === "brand" ? "bold " : ""}${fontSize}px sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = "var(--color-text, #333)";
      ctx.fillText(label, node.x, node.y + r + 2);
    }
  }, [selected]);

  const connections = selected && data ? data.edges.filter(
    e => e.source === selected.id || e.target === selected.id
  ).map(e => {
    const otherId = e.source === selected.id ? e.target : e.source;
    const otherNode = data.nodes.find(n => n.id === otherId);
    return otherNode ? { ...otherNode, weight: e.weight } : null;
  }).filter(Boolean).sort((a, b) => b.weight - a.weight) : [];

  return (
    <main className="flex-1 flex overflow-hidden bg-[var(--color-bg)]">
      {/* Graph Canvas */}
      <div className="flex-1 relative" ref={containerRef}>
        <div className="absolute top-4 left-4 z-10 flex gap-2">
          {["all", "material", "color", "category"].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 text-xs rounded-md border transition-colors ${
                filter === f
                  ? "bg-[var(--color-primary)] text-white border-[var(--color-primary)]"
                  : "bg-white border-[var(--color-border)] text-[var(--color-text-secondary)] hover:bg-gray-50"
              }`}
            >
              {f === "all" ? "All" : f.charAt(0).toUpperCase() + f.slice(1) + "s"}
            </button>
          ))}
        </div>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 z-10 bg-white/90 border border-[var(--color-border)] rounded-md p-3 flex flex-col gap-1.5">
          {LEGEND.map(l => <LegendItem key={l.type} {...l} />)}
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
      <aside className="w-[280px] border-l border-[var(--color-border)] bg-white p-5 overflow-y-auto shrink-0">
        <h2 className="font-['Lora'] text-base font-semibold mb-4">Node Detail</h2>
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
          <p className="text-sm text-[var(--color-text-muted)]">Click a node in the graph to view its connections and details.</p>
        )}
      </aside>
    </main>
  );
}
