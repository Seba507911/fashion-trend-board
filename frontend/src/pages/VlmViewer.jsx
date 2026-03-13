import { useQuery } from "@tanstack/react-query";
import { useState, useMemo } from "react";
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

const SEASON_LABELS = {
  "spring-summer-2026": "SS26",
  "fall-winter-2026": "FW26",
  "spring-summer-2025": "SS25",
  "fall-winter-2025": "FW25",
  "spring-summer-2024": "SS24",
  "fall-winter-2024": "FW24",
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

function FilterSelect({ label, value, onChange, options }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-[10px] font-semibold tracking-wider text-[var(--color-text-muted)] uppercase">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="text-xs border border-[var(--color-border)] rounded-md px-2.5 py-1.5 bg-white text-[var(--color-text-secondary)] min-w-[130px]"
      >
        <option value="">All</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
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
          {SEASON_LABELS[look.season] || look.season} &middot; Look #{look.look_number}
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
                {SEASON_LABELS[look.season] || look.season} &middot; Look #{look.look_number}
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

function extractFilterOptions(data) {
  const designers = new Set();
  const seasons = new Set();
  const silhouettes = new Set();
  const colors = new Set();
  const materials = new Set();
  const textures = new Set();

  for (const look of data) {
    designers.add(look.designer);
    seasons.add(look.season);
    if (look.overall_silhouette) silhouettes.add(look.overall_silhouette.toLowerCase());
    look.dominant_colors?.forEach((c) => colors.add(c.toLowerCase()));
    look.key_materials?.forEach((m) => materials.add(m.toLowerCase()));
    look.items?.forEach((item) => {
      if (item.texture) textures.add(item.texture.toLowerCase());
    });
  }

  const toOpts = (set, labelFn) =>
    [...set].sort().map((v) => ({ value: v, label: labelFn ? labelFn(v) : v }));

  return {
    designers: toOpts(designers),
    seasons: toOpts(seasons, (s) => SEASON_LABELS[s] || s),
    silhouettes: toOpts(silhouettes),
    colors: toOpts(colors),
    materials: toOpts(materials),
    textures: toOpts(textures),
  };
}

export default function VlmViewer() {
  const { data, isLoading, error } = useVlmLabels();
  const [selected, setSelected] = useState(null);

  const [fDesigner, setFDesigner] = useState("");
  const [fSeason, setFSeason] = useState("");
  const [fSilhouette, setFSilhouette] = useState("");
  const [fColor, setFColor] = useState("");
  const [fMaterial, setFMaterial] = useState("");
  const [fTexture, setFTexture] = useState("");

  const filterOptions = useMemo(() => {
    if (!data?.length) return null;
    return extractFilterOptions(data);
  }, [data]);

  const filtered = useMemo(() => {
    if (!data?.length) return [];
    return data.filter((look) => {
      if (fDesigner && look.designer !== fDesigner) return false;
      if (fSeason && look.season !== fSeason) return false;
      if (fSilhouette && look.overall_silhouette?.toLowerCase() !== fSilhouette) return false;
      if (fColor && !look.dominant_colors?.some((c) => c.toLowerCase() === fColor)) return false;
      if (fMaterial && !look.key_materials?.some((m) => m.toLowerCase() === fMaterial)) return false;
      if (fTexture && !look.items?.some((item) => item.texture?.toLowerCase() === fTexture)) return false;
      return true;
    });
  }, [data, fDesigner, fSeason, fSilhouette, fColor, fMaterial, fTexture]);

  const hasActiveFilter = fDesigner || fSeason || fSilhouette || fColor || fMaterial || fTexture;

  const clearFilters = () => {
    setFDesigner("");
    setFSeason("");
    setFSilhouette("");
    setFColor("");
    setFMaterial("");
    setFTexture("");
  };

  if (isLoading) return <div className="flex-1 flex items-center justify-center text-[var(--color-text-muted)]">Loading VLM results...</div>;
  if (error) return <div className="flex-1 flex items-center justify-center text-red-500">Error loading data</div>;
  if (!data?.length) return <div className="flex-1 flex items-center justify-center text-[var(--color-text-muted)]">No VLM labels yet</div>;

  return (
    <main className="flex-1 p-6 overflow-y-auto">
      <div className="mb-4">
        <h1 className="font-['Lora'] text-xl font-bold tracking-wide">VLM Label Viewer</h1>
        <p className="text-xs text-[var(--color-text-muted)] mt-1">
          {filtered.length}{hasActiveFilter ? ` / ${data.length}` : ""} looks labeled &middot; Claude Vision analysis results
        </p>
      </div>

      {/* Filters */}
      {filterOptions && (
        <div className="bg-white border border-[var(--color-border)] rounded-md p-4 mb-5">
          <div className="flex items-end gap-3 flex-wrap">
            <FilterSelect label="Designer" value={fDesigner} onChange={setFDesigner} options={filterOptions.designers} />
            <FilterSelect label="Season" value={fSeason} onChange={setFSeason} options={filterOptions.seasons} />
            <FilterSelect label="Silhouette" value={fSilhouette} onChange={setFSilhouette} options={filterOptions.silhouettes} />
            <FilterSelect label="Color" value={fColor} onChange={setFColor} options={filterOptions.colors} />
            <FilterSelect label="Material" value={fMaterial} onChange={setFMaterial} options={filterOptions.materials} />
            <FilterSelect label="Texture" value={fTexture} onChange={setFTexture} options={filterOptions.textures} />
            {hasActiveFilter && (
              <button
                onClick={clearFilters}
                className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text)] px-3 py-1.5 border border-[var(--color-border)] rounded-md hover:bg-gray-50 transition-colors"
              >
                Clear all
              </button>
            )}
          </div>
        </div>
      )}

      {filtered.length === 0 ? (
        <div className="text-center py-16 text-sm text-[var(--color-text-muted)]">
          No looks match the current filters.
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filtered.map((look) => (
            <LookCard key={look.id} look={look} onClick={setSelected} />
          ))}
        </div>
      )}

      <DetailModal look={selected} onClose={() => setSelected(null)} />
    </main>
  );
}
