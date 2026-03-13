import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

function useVlmLabels() {
  return useQuery({
    queryKey: ["vlm-labels"],
    queryFn: () => api.get("/vlm").then((r) => r.data),
  });
}

const TEXTURE_COLORS = {
  matte: "#6B7280", glossy: "#3B82F6", textured: "#F59E0B",
  quilted: "#8B5CF6", woven: "#10B981", smooth: "#EC4899",
  distressed: "#EF4444", embossed: "#F97316",
};

const SHAPE_ICONS = {
  structured: "◼", unstructured: "◻", round: "●", square: "■",
  asymmetric: "◆", geometric: "▲", organic: "○",
};

function Tag({ children, color = "#6B7280" }) {
  return (
    <span
      className="inline-block px-2 py-0.5 rounded-full text-[10px] font-medium text-white mr-1 mb-1"
      style={{ backgroundColor: color }}
    >
      {children}
    </span>
  );
}

function ColorDot({ color }) {
  const CSS_COLORS = {
    black: "#000", white: "#fff", navy: "#001f3f", burgundy: "#800020",
    beige: "#F5F5DC", blue: "#2563EB", gray: "#6B7280", grey: "#6B7280",
    teal: "#14B8A6", orange: "#F97316", red: "#EF4444", green: "#22C55E",
    brown: "#92400E", cream: "#FFFDD0", silver: "#C0C0C0", pink: "#EC4899",
    yellow: "#EAB308", purple: "#8B5CF6", gold: "#D4A017",
  };
  const bg = CSS_COLORS[color?.toLowerCase()] || "#9CA3AF";
  return (
    <span className="inline-flex items-center gap-1 mr-2">
      <span
        className="w-3 h-3 rounded-full border border-gray-300 inline-block"
        style={{ backgroundColor: bg }}
      />
      <span className="text-[11px] text-[var(--color-text-muted)]">{color}</span>
    </span>
  );
}

function LookCard({ look, onClick }) {
  return (
    <div
      className="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden cursor-pointer hover:border-[var(--color-accent)] transition-colors"
      onClick={() => onClick(look)}
    >
      <div className="aspect-[3/4] overflow-hidden bg-gray-100">
        <img
          src={look.image_url}
          alt={`${look.designer} Look #${look.look_number}`}
          className="w-full h-full object-cover"
          loading="lazy"
        />
      </div>
      <div className="p-3">
        <div className="font-['Lora'] text-sm font-semibold truncate">{look.designer}</div>
        <div className="text-[10px] text-[var(--color-text-muted)] mb-2">
          {look.season} &middot; Look #{look.look_number}
        </div>
        <div className="flex items-center gap-1 mb-1">
          {look.dominant_colors?.map((c, i) => <ColorDot key={i} color={c} />)}
        </div>
        <Tag color="#6366F1">{look.overall_silhouette}</Tag>
        {look.key_materials?.map((m, i) => (
          <Tag key={i} color="#0D9488">{m}</Tag>
        ))}
      </div>
    </div>
  );
}

function DetailModal({ look, onClose }) {
  if (!look) return null;
  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div
        className="bg-white rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto flex flex-col md:flex-row shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Image */}
        <div className="md:w-1/2 bg-gray-100 flex-shrink-0">
          <img
            src={look.image_url}
            alt={`${look.designer} Look #${look.look_number}`}
            className="w-full h-full object-cover"
          />
        </div>

        {/* Info */}
        <div className="md:w-1/2 p-6 overflow-y-auto">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="font-['Lora'] text-lg font-bold">{look.designer}</h2>
              <p className="text-xs text-[var(--color-text-muted)]">
                {look.season} &middot; Look #{look.look_number}
              </p>
            </div>
            <button onClick={onClose} className="text-[var(--color-text-muted)] hover:text-[var(--color-text)] text-xl">&times;</button>
          </div>

          {/* Overall */}
          <div className="mb-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)] mb-2">Overall</h3>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-medium">Silhouette:</span>
              <Tag color="#6366F1">{look.overall_silhouette}</Tag>
            </div>
            <div className="flex items-center gap-1 mb-2">
              <span className="text-sm font-medium mr-1">Colors:</span>
              {look.dominant_colors?.map((c, i) => <ColorDot key={i} color={c} />)}
            </div>
            <div className="flex items-center flex-wrap gap-1">
              <span className="text-sm font-medium mr-1">Materials:</span>
              {look.key_materials?.map((m, i) => <Tag key={i} color="#0D9488">{m}</Tag>)}
            </div>
          </div>

          {/* Items */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)] mb-2">
              Items ({look.items?.length || 0})
            </h3>
            <div className="space-y-2">
              {look.items?.map((item, i) => (
                <div key={i} className="bg-[var(--color-bg)] rounded-lg p-3 border border-[var(--color-border)]">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold capitalize">{item.item}</span>
                    <span className="text-[10px] text-[var(--color-text-muted)]">{item.size}</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    <ColorDot color={item.color} />
                    <Tag color={TEXTURE_COLORS[item.texture] || "#6B7280"}>{item.texture}</Tag>
                    <Tag color="#78716C">
                      {SHAPE_ICONS[item.shape] || "?"} {item.shape}
                    </Tag>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Meta */}
          <div className="mt-4 pt-3 border-t border-[var(--color-border)]">
            <p className="text-[10px] text-[var(--color-text-muted)]">
              Model: {look.model_used} &middot; Labeled: {look.created_at?.slice(0, 16)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function VlmViewer() {
  const { data, isLoading, error } = useVlmLabels();
  const [selected, setSelected] = useState(null);

  if (isLoading) return <div className="flex-1 flex items-center justify-center text-[var(--color-text-muted)]">Loading VLM results...</div>;
  if (error) return <div className="flex-1 flex items-center justify-center text-red-500">Error loading data</div>;
  if (!data?.length) return <div className="flex-1 flex items-center justify-center text-[var(--color-text-muted)]">No VLM labels yet</div>;

  return (
    <main className="flex-1 p-6 overflow-y-auto">
      <div className="mb-6">
        <h1 className="font-['Lora'] text-xl font-bold tracking-wide">VLM Label Viewer</h1>
        <p className="text-xs text-[var(--color-text-muted)] mt-1">
          {data.length} looks labeled &middot; Claude Vision analysis results
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {data.map((look) => (
          <LookCard key={look.id} look={look} onClick={setSelected} />
        ))}
      </div>

      <DetailModal look={selected} onClose={() => setSelected(null)} />
    </main>
  );
}
