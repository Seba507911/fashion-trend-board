import { useEffect, useState, useCallback, useRef, useMemo } from "react";
import ForceGraph2D from "react-force-graph-2d";

const SOURCE_LABELS = {
  musinsa: "Musinsa",
  product: "Market Products",
  runway_tagwalk: "Runway (TagWalk)",
  runway_vogue: "Runway (Vogue)",
};

const SOURCE_COLORS = {
  musinsa: "#22c55e",
  product: "#f59e0b",
  runway_tagwalk: "#8b5cf6",
  runway_vogue: "#ec4899",
};

function StatsPanel({ stats }) {
  if (!stats) return <div className="text-gray-400 text-sm">Loading stats...</div>;
  return (
    <div className="bg-white border rounded p-4">
      <div className="flex items-baseline gap-3 mb-3">
        <h2 className="text-base font-semibold">Embedding Coverage</h2>
        <span className="text-xs text-gray-500">model: {stats.model_version}</span>
        <span className="ml-auto text-sm">
          total <b className="text-blue-600">{stats.total_embedded.toLocaleString()}</b>
        </span>
      </div>
      <table className="w-full text-sm">
        <thead className="text-gray-500 border-b">
          <tr>
            <th className="text-left py-1">Source</th>
            <th className="text-right">Embedded</th>
            <th className="text-right">Failed</th>
            <th className="text-right">Skipped</th>
            <th className="text-right">Coverage</th>
          </tr>
        </thead>
        <tbody>
          {stats.rows.map((r) => {
            const total = r.embedded + r.failed + r.skipped;
            const pct = total ? ((r.embedded / total) * 100).toFixed(1) : "0";
            return (
              <tr key={r.source_type} className="border-b last:border-0">
                <td className="py-1">{SOURCE_LABELS[r.source_type] || r.source_type}</td>
                <td className="text-right tabular-nums">{r.embedded.toLocaleString()}</td>
                <td className="text-right tabular-nums text-red-500">{r.failed.toLocaleString()}</td>
                <td className="text-right tabular-nums text-gray-400">{r.skipped.toLocaleString()}</td>
                <td className="text-right tabular-nums">{pct}%</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function itemSubtitle(item) {
  if (!item) return "";
  if (item.source_type === "musinsa" || item.source_type === "product") {
    return `${item.brand || ""}${item.name ? " · " + item.name : ""}`;
  }
  return `${item.designer || ""} · ${item.season || ""}${item.look_number ? ` · #${item.look_number}` : ""}`;
}

function ItemCard({ item, score, onClick, highlighted }) {
  return (
    <button
      onClick={onClick}
      className={`group relative bg-white border rounded overflow-hidden hover:shadow-md transition text-left ${
        highlighted ? "ring-2 ring-blue-500" : ""
      }`}
    >
      <div className="aspect-[3/4] bg-gray-100 overflow-hidden">
        <img
          src={item.image_url}
          alt=""
          loading="lazy"
          className="w-full h-full object-cover group-hover:scale-105 transition"
          onError={(e) => { e.currentTarget.style.opacity = "0.2"; }}
        />
        {score !== undefined && (
          <div className="absolute top-1 right-1 bg-black/70 text-white text-xs px-1.5 py-0.5 rounded">
            {score.toFixed(3)}
          </div>
        )}
        <div className="absolute top-1 left-1 bg-white/90 text-[10px] px-1.5 py-0.5 rounded uppercase tracking-wide">
          {item.source_type.replace("runway_", "")}
        </div>
      </div>
      <div className="p-1.5 text-[11px] leading-tight text-gray-700 truncate">
        {itemSubtitle(item)}
      </div>
    </button>
  );
}

function GraphPanel({ graph, onPickNode }) {
  const fgRef = useRef();
  const containerRef = useRef();
  const [size, setSize] = useState({ width: 800, height: 560 });
  const imgCache = useRef(new Map());

  useEffect(() => {
    const update = () => {
      if (containerRef.current) {
        setSize({
          width: containerRef.current.clientWidth,
          height: 560,
        });
      }
    };
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  // Normalize to ForceGraph2D shape
  const data = useMemo(() => {
    if (!graph) return { nodes: [], links: [] };
    return {
      nodes: graph.nodes.map((n) => ({ ...n })),
      links: graph.links.map((l) => ({ ...l })),
    };
  }, [graph]);

  const drawNode = useCallback((node, ctx, scale) => {
    const r = node.is_query ? 18 : 10 + node.similarity_to_query * 10;
    let img = imgCache.current.get(node.image_url);
    if (img && img.complete && img.naturalWidth > 0) {
      ctx.save();
      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, 2 * Math.PI, false);
      ctx.closePath();
      ctx.clip();
      ctx.drawImage(img, node.x - r, node.y - r, r * 2, r * 2);
      ctx.restore();
    } else {
      if (!img) {
        img = new Image();
        img.crossOrigin = "anonymous";
        img.src = node.image_url;
        imgCache.current.set(node.image_url, img);
      }
      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, 2 * Math.PI, false);
      ctx.fillStyle = "#e5e7eb";
      ctx.fill();
    }
    // Border by source
    ctx.strokeStyle = node.is_query ? "#2563eb" : SOURCE_COLORS[node.source_type] || "#999";
    ctx.lineWidth = node.is_query ? 3 / scale : 2 / scale;
    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
    ctx.stroke();
  }, []);

  if (!graph) return <div className="text-sm text-gray-400 p-4">Click an image to see graph.</div>;

  return (
    <div ref={containerRef} className="bg-gray-50 border rounded">
      <ForceGraph2D
        ref={fgRef}
        graphData={data}
        width={size.width}
        height={size.height}
        nodeRelSize={6}
        nodeCanvasObject={drawNode}
        nodeCanvasObjectMode={() => "replace"}
        nodePointerAreaPaint={(node, color, ctx) => {
          const r = node.is_query ? 18 : 10 + node.similarity_to_query * 10;
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
          ctx.fill();
        }}
        nodeLabel={(n) => `${n.label}${n.is_query ? " (query)" : ""}\nsim=${n.similarity_to_query.toFixed(3)}`}
        linkWidth={(l) => Math.max(0.5, (l.value - 0.6) * 6)}
        linkColor={(l) => `rgba(59,130,246,${Math.max(0.1, (l.value - 0.5))})`}
        cooldownTicks={60}
        onNodeClick={(n) => { if (!n.is_query) onPickNode(n.id); }}
      />
      <div className="px-3 py-1.5 border-t bg-white text-[11px] flex flex-wrap gap-3 text-gray-600">
        <span className="font-medium">Legend:</span>
        {Object.entries(SOURCE_LABELS).map(([k, v]) => (
          <span key={k} className="flex items-center gap-1">
            <span className="inline-block w-3 h-3 rounded-full border-2" style={{ borderColor: SOURCE_COLORS[k] }} />
            {v}
          </span>
        ))}
        <span className="ml-auto">노드 클릭 → 그 이미지를 새 쿼리로 검색</span>
      </div>
    </div>
  );
}

export default function VectorExplorer() {
  const [stats, setStats] = useState(null);
  const [pickerSource, setPickerSource] = useState("runway_vogue");
  const [picks, setPicks] = useState([]);
  const [picksLoading, setPicksLoading] = useState(false);
  const [query, setQuery] = useState(null);
  const [results, setResults] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [filterSource, setFilterSource] = useState("");
  const [crossSourceOnly, setCrossSourceOnly] = useState(false);
  const [excludeSameBrand, setExcludeSameBrand] = useState(true);
  const [viewMode, setViewMode] = useState("grid");  // 'grid' | 'graph'

  useEffect(() => {
    fetch("/api/embeddings/stats").then((r) => r.json()).then(setStats);
  }, []);

  const loadPicks = useCallback(() => {
    setPicksLoading(true);
    fetch(`/api/embeddings/picks?source_type=${pickerSource}&n=12`)
      .then((r) => r.json())
      .then((data) => { setPicks(data); setPicksLoading(false); });
  }, [pickerSource]);

  useEffect(() => { loadPicks(); }, [loadPicks]);

  const fetchSimilar = useCallback((qid) => {
    setResultsLoading(true);
    const params = new URLSearchParams({
      id: String(qid),
      top: viewMode === "graph" ? "15" : "12",
      exclude_same_brand: String(excludeSameBrand),
    });
    if (filterSource) params.set("filter_source", filterSource);
    if (crossSourceOnly) params.set("exclude_self_source", "true");

    const endpoint = viewMode === "graph" ? "graph" : "similar";
    fetch(`/api/embeddings/${endpoint}?${params}`)
      .then((r) => r.json())
      .then((data) => {
        if (viewMode === "graph") {
          setGraphData(data);
          // Also keep query meta for header
          const q = data.nodes?.find((n) => n.is_query);
          if (q) setQuery({ id: q.id, source_type: q.source_type, image_url: q.image_url, ...q.meta });
          setResults(null);
        } else {
          setQuery(data.query);
          setResults(data.results);
          setGraphData(null);
        }
        setResultsLoading(false);
      });
  }, [filterSource, crossSourceOnly, excludeSameBrand, viewMode]);

  useEffect(() => {
    if (query?.id) fetchSimilar(query.id);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterSource, crossSourceOnly, excludeSameBrand, viewMode]);

  return (
    <div className="flex-1 p-6 bg-gray-50 overflow-y-auto">
      <div className="max-w-7xl mx-auto space-y-6">
        <div>
          <h1 className="text-xl font-bold mb-1">Vector Explorer</h1>
          <p className="text-sm text-gray-600">
            Marqo-FashionSigLIP-v1 임베딩으로 이미지를 골라 유사한 다른 이미지를 찾습니다.
            기본은 같은 브랜드/디자이너 결과를 제외해 cross-brand 비교에 집중합니다.
          </p>
        </div>

        <StatsPanel stats={stats} />

        <div className="bg-white border rounded p-4">
          <div className="flex items-center gap-3 mb-3 flex-wrap">
            <h2 className="text-base font-semibold">1. 쿼리 이미지 선택</h2>
            <div className="ml-auto flex items-center gap-2">
              {Object.entries(SOURCE_LABELS).map(([k, v]) => (
                <button
                  key={k}
                  onClick={() => setPickerSource(k)}
                  className={`text-xs px-2.5 py-1 rounded border ${
                    pickerSource === k ? "bg-blue-600 text-white border-blue-600" : "bg-white border-gray-300 text-gray-700"
                  }`}
                >
                  {v}
                </button>
              ))}
              <button
                onClick={loadPicks}
                className="text-xs px-2.5 py-1 rounded border bg-white border-gray-300 hover:bg-gray-50"
              >
                ↻ 새로 뽑기
              </button>
            </div>
          </div>
          {picksLoading ? (
            <div className="text-sm text-gray-400">Loading...</div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-2">
              {picks.map((p) => (
                <ItemCard
                  key={p.id}
                  item={p}
                  highlighted={query?.id === p.id}
                  onClick={() => fetchSimilar(p.id)}
                />
              ))}
            </div>
          )}
        </div>

        {query && (
          <div className="bg-white border rounded p-4">
            <div className="flex items-center gap-3 mb-3 flex-wrap">
              <h2 className="text-base font-semibold">2. 유사 이미지</h2>
              <span className="text-xs text-gray-500">
                {viewMode === "grid" ? `${results?.length || 0}건` : `${graphData?.nodes?.length || 0}노드 · ${graphData?.links?.length || 0}링크`}
              </span>
              <div className="ml-auto flex items-center gap-2 flex-wrap">
                <div className="flex items-center border rounded overflow-hidden">
                  <button
                    onClick={() => setViewMode("grid")}
                    className={`text-xs px-2.5 py-1 ${viewMode === "grid" ? "bg-gray-800 text-white" : "bg-white text-gray-700"}`}
                  >
                    Grid
                  </button>
                  <button
                    onClick={() => setViewMode("graph")}
                    className={`text-xs px-2.5 py-1 ${viewMode === "graph" ? "bg-gray-800 text-white" : "bg-white text-gray-700"}`}
                  >
                    Graph
                  </button>
                </div>
                <select
                  value={filterSource}
                  onChange={(e) => setFilterSource(e.target.value)}
                  className="text-xs border rounded px-2 py-1"
                >
                  <option value="">All sources</option>
                  {Object.entries(SOURCE_LABELS).map(([k, v]) => (
                    <option key={k} value={k}>{v}만</option>
                  ))}
                </select>
                <label className="text-xs flex items-center gap-1.5">
                  <input
                    type="checkbox"
                    checked={excludeSameBrand}
                    onChange={(e) => setExcludeSameBrand(e.target.checked)}
                  />
                  같은 브랜드/디자이너 제외
                </label>
                <label className="text-xs flex items-center gap-1.5">
                  <input
                    type="checkbox"
                    checked={crossSourceOnly}
                    onChange={(e) => setCrossSourceOnly(e.target.checked)}
                  />
                  다른 소스만
                </label>
              </div>
            </div>

            {viewMode === "grid" ? (
              <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-4">
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-1.5">Query</div>
                  <ItemCard item={query} />
                </div>
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-1.5">Results</div>
                  {resultsLoading ? (
                    <div className="text-sm text-gray-400">Loading...</div>
                  ) : results?.length ? (
                    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-2">
                      {results.map((r) => (
                        <ItemCard
                          key={r.id}
                          item={r}
                          score={r.similarity}
                          onClick={() => fetchSimilar(r.id)}
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-gray-400">필터 조건에 맞는 결과가 없습니다.</div>
                  )}
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-4">
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-1.5">Query</div>
                  <ItemCard item={query} />
                </div>
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-1.5">Similarity Graph</div>
                  {resultsLoading ? (
                    <div className="text-sm text-gray-400">Loading...</div>
                  ) : (
                    <GraphPanel graph={graphData} onPickNode={fetchSimilar} />
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
