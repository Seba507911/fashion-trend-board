import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

function useRunwayDesigners() {
  return useQuery({
    queryKey: ["runway", "designers"],
    queryFn: () => api.get("/runway/designers").then(r => r.data),
  });
}

function useRunwayLooks({ designer, season } = {}) {
  return useQuery({
    queryKey: ["runway", "looks", { designer, season }],
    queryFn: () =>
      api.get("/runway", { params: { designer, season, limit: 120 } }).then(r => r.data),
  });
}

function useRunwaySeasons() {
  return useQuery({
    queryKey: ["runway", "seasons"],
    queryFn: () => api.get("/runway/seasons").then(r => r.data),
  });
}

function LookCard({ look, onClick }) {
  return (
    <button
      onClick={() => onClick(look)}
      className="group relative bg-white border border-[var(--color-border)] rounded-md overflow-hidden hover:shadow-md transition-shadow text-left"
    >
      <div className="aspect-[2/3] bg-gray-100 overflow-hidden">
        <img
          src={look.thumbnail_url || look.image_url}
          alt={`${look.designer} ${look.season_label} Look #${look.look_number}`}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
          onError={(e) => {
            e.target.style.display = "none";
          }}
        />
      </div>
      <div className="p-2.5">
        <span className="text-[10px] font-semibold tracking-wider text-[var(--color-text-muted)] uppercase">
          Look {look.look_number}
        </span>
      </div>
    </button>
  );
}

function LookModal({ look, onClose }) {
  if (!look) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-8"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg overflow-hidden max-w-[480px] max-h-[90vh] flex flex-col shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="overflow-y-auto flex-1">
          <img
            src={look.image_url}
            alt={`${look.designer} Look #${look.look_number}`}
            className="w-full"
          />
        </div>
        <div className="p-4 border-t border-[var(--color-border)] flex items-center justify-between">
          <div>
            <p className="font-['Lora'] font-semibold text-sm">{look.designer}</p>
            <p className="text-xs text-[var(--color-text-secondary)]">
              {look.season_label} &middot; {look.city} &middot; Look #{look.look_number}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text)] px-3 py-1.5 border border-[var(--color-border)] rounded"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Runway() {
  const { data: designers = [] } = useRunwayDesigners();
  const { data: seasons = [] } = useRunwaySeasons();
  const [selectedDesigner, setSelectedDesigner] = useState(null);
  const [selectedSeason, setSelectedSeason] = useState(null);
  const [selectedLook, setSelectedLook] = useState(null);

  // Auto-select first designer (alphabetically) on initial load
  useEffect(() => {
    if (designers.length > 0 && selectedDesigner === null) {
      const sorted = [...designers].sort((a, b) => a.designer.localeCompare(b.designer));
      setSelectedDesigner(sorted[0].designer_slug);
    }
  }, [designers, selectedDesigner]);

  const { data: looks = [], isLoading } = useRunwayLooks({
    designer: selectedDesigner,
    season: selectedSeason,
  });

  // 디자이너별로 그룹핑
  const grouped = {};
  looks.forEach((look) => {
    const key = `${look.designer_slug}__${look.season}`;
    if (!grouped[key]) {
      grouped[key] = {
        designer: look.designer,
        designer_slug: look.designer_slug,
        season: look.season,
        season_label: look.season_label,
        city: look.city,
        looks: [],
      };
    }
    grouped[key].looks.push(look);
  });

  const groups = Object.values(grouped).sort((a, b) => {
    if (a.designer < b.designer) return -1;
    if (a.designer > b.designer) return 1;
    return b.season.localeCompare(a.season);
  });

  const isEmpty = !isLoading && looks.length === 0;

  return (
    <main className="flex-1 p-8 overflow-y-auto bg-[var(--color-bg)]">
      <div className="max-w-[1200px] mx-auto">
        <h1 className="font-['Lora'] text-xl font-semibold tracking-wide mb-1">Runway</h1>
        <p className="text-sm text-[var(--color-text-secondary)] mb-6">
          Collection looks from major fashion weeks &middot; Source: TagWalk
        </p>

        {/* Filters */}
        <div className="flex gap-3 mb-6 flex-wrap">
          {/* Designer filter */}
          <select
            value={selectedDesigner || ""}
            onChange={(e) => setSelectedDesigner(e.target.value || null)}
            className="text-xs px-3 py-2 border border-[var(--color-border)] rounded-md bg-white text-[var(--color-text)]"
          >
            <option value="" disabled>— Select Designer —</option>
            {[...designers].sort((a, b) => a.designer.localeCompare(b.designer)).map((d) => (
              <option key={d.designer_slug} value={d.designer_slug}>
                {d.designer} ({d.look_count} looks)
              </option>
            ))}
          </select>

          {/* Season filter */}
          <select
            value={selectedSeason || ""}
            onChange={(e) => setSelectedSeason(e.target.value || null)}
            className="text-xs px-3 py-2 border border-[var(--color-border)] rounded-md bg-white text-[var(--color-text)]"
          >
            <option value="">All Seasons</option>
            {seasons.map((s) => (
              <option key={s.season} value={s.season}>
                {s.season_label || s.season}
              </option>
            ))}
          </select>

          {/* Stats */}
          <div className="ml-auto text-xs text-[var(--color-text-muted)] self-center">
            {looks.length} looks
            {designers.length > 0 && ` · ${designers.length} designers`}
          </div>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="text-sm text-[var(--color-text-muted)] py-20 text-center">Loading runway looks...</div>
        ) : isEmpty ? (
          <div className="text-center py-20">
            <p className="text-sm text-[var(--color-text-muted)] mb-2">No runway data yet</p>
            <p className="text-xs text-[var(--color-text-muted)]">
              Run <code className="bg-gray-100 px-1.5 py-0.5 rounded">python scripts/crawl_tagwalk.py</code> to fetch looks
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-10">
            {groups.map((group) => (
              <section key={`${group.designer_slug}__${group.season}`}>
                <div className="flex items-baseline gap-3 mb-4">
                  <h2 className="font-['Lora'] text-base font-semibold">{group.designer}</h2>
                  <span className="text-xs text-[var(--color-text-secondary)]">
                    {group.season_label}
                  </span>
                  {group.city && (
                    <span className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider">
                      {group.city}
                    </span>
                  )}
                  <span className="text-[10px] text-[var(--color-text-muted)]">
                    {group.looks.length} looks
                  </span>
                </div>

                <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6 lg:grid-cols-8 gap-3">
                  {group.looks.map((look) => (
                    <LookCard key={look.id} look={look} onClick={setSelectedLook} />
                  ))}
                </div>
              </section>
            ))}
          </div>
        )}
      </div>

      <LookModal look={selectedLook} onClose={() => setSelectedLook(null)} />
    </main>
  );
}
