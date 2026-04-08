import { useQuery } from "@tanstack/react-query";
import { useState, useEffect, useMemo } from "react";
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

function useVogueShows(params) {
  return useQuery({
    queryKey: ["vogue-runway", "shows", params],
    queryFn: () => api.get("/vogue-runway/shows", { params }).then(r => r.data),
  });
}

function useVogueShowDetail(showId) {
  return useQuery({
    queryKey: ["vogue-runway", "show", showId],
    queryFn: () => api.get(`/vogue-runway/shows/${encodeURIComponent(showId)}`).then(r => r.data),
    enabled: !!showId,
  });
}

function useVogueStats() {
  return useQuery({
    queryKey: ["vogue-runway", "stats"],
    queryFn: () => api.get("/vogue-runway/stats").then(r => r.data),
  });
}

const TYPE_LABELS = {
  collection: "Collection",
  detail: "Details",
  backstage: "Backstage",
  beauty: "Beauty",
  atmosphere: "Atmosphere",
  front_row: "Front Row",
};

const TYPE_COLORS = {
  collection: "bg-blue-100 text-blue-700 ring-blue-300",
  detail: "bg-amber-100 text-amber-700 ring-amber-300",
  backstage: "bg-purple-100 text-purple-700 ring-purple-300",
  beauty: "bg-pink-100 text-pink-700 ring-pink-300",
  atmosphere: "bg-green-100 text-green-700 ring-green-300",
  front_row: "bg-rose-100 text-rose-700 ring-rose-300",
};

function ImageCard({ image, onClick }) {
  return (
    <button
      onClick={() => onClick(image)}
      className="group relative bg-white border border-[var(--color-border)] rounded-md overflow-hidden hover:shadow-md transition-shadow text-left"
    >
      <div className="aspect-[2/3] bg-gray-100 overflow-hidden">
        <img
          src={image.thumbnail_url || image.image_url_md || image.image_url}
          alt={image.alt_text || `${image.designer} ${image.image_type} #${image.look_number}`}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
          onError={(e) => { e.target.style.display = "none"; }}
        />
      </div>
      <div className="p-2 flex items-center justify-between gap-1">
        <span className="text-[10px] font-semibold tracking-wider text-[var(--color-text-muted)] uppercase truncate">
          {image.alt_text || `#${image.look_number}`}
        </span>
        <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-medium shrink-0 ${TYPE_COLORS[image.image_type] || "bg-gray-100 text-gray-600"}`}>
          {TYPE_LABELS[image.image_type] || image.image_type}
        </span>
      </div>
    </button>
  );
}

function ImageModal({ image, onClose }) {
  if (!image) return null;
  return (
    <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-8" onClick={onClose}>
      <div className="bg-white rounded-lg overflow-hidden max-w-[520px] max-h-[90vh] flex flex-col shadow-2xl" onClick={e => e.stopPropagation()}>
        <div className="overflow-y-auto flex-1">
          <img src={image.image_url} alt={image.alt_text} className="w-full" />
        </div>
        <div className="p-4 border-t border-[var(--color-border)] flex items-center justify-between">
          <div>
            <p className="font-['Lora'] font-semibold text-sm">{image.designer}</p>
            <p className="text-xs text-[var(--color-text-secondary)]">
              {image.season} &middot; {TYPE_LABELS[image.image_type] || image.image_type} &middot; #{image.look_number}
            </p>
          </div>
          <button onClick={onClose} className="text-xs px-3 py-1.5 rounded border border-[var(--color-border)] hover:bg-gray-50">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default function VogueRunway() {
  const [selectedDesigner, setSelectedDesigner] = useState(null);
  const [selectedSeason, setSelectedSeason] = useState(null);
  const [selectedType, setSelectedType] = useState(null);
  const [imageTypeFilter, setImageTypeFilter] = useState("all");
  const [modalImage, setModalImage] = useState(null);

  const { data: allShows = [], isLoading: showsLoading } = useVogueShows();
  const { data: stats } = useVogueStats();

  // Derive unique designers, seasons, collection types from shows
  const designers = useMemo(() => {
    const map = {};
    allShows.forEach(s => {
      if (!map[s.designer_slug]) {
        map[s.designer_slug] = { slug: s.designer_slug, name: s.designer, showCount: 0, imageCount: 0 };
      }
      map[s.designer_slug].showCount++;
      map[s.designer_slug].imageCount += (s.total_looks || 0) + (s.total_details || 0);
    });
    return Object.values(map).sort((a, b) => a.name.localeCompare(b.name));
  }, [allShows]);

  const seasons = useMemo(() => {
    const set = new Set();
    allShows.forEach(s => set.add(s.season));
    return [...set].sort().reverse();
  }, [allShows]);

  const collectionTypes = useMemo(() => {
    const set = new Set();
    const filtered = allShows.filter(s =>
      (!selectedDesigner || s.designer_slug === selectedDesigner) &&
      (!selectedSeason || s.season === selectedSeason)
    );
    filtered.forEach(s => set.add(s.collection_type));
    return [...set].sort();
  }, [allShows, selectedDesigner, selectedSeason]);

  // Auto-select first designer
  useEffect(() => {
    if (designers.length > 0 && selectedDesigner === null) {
      setSelectedDesigner(designers[0].slug);
    }
  }, [designers, selectedDesigner]);

  // Find matching show
  const matchingShows = useMemo(() => {
    return allShows.filter(s =>
      (!selectedDesigner || s.designer_slug === selectedDesigner) &&
      (!selectedSeason || s.season === selectedSeason) &&
      (!selectedType || s.collection_type === selectedType)
    );
  }, [allShows, selectedDesigner, selectedSeason, selectedType]);

  const selectedShowId = matchingShows.length === 1 ? matchingShows[0].id : null;
  const { data: showDetail, isLoading: detailLoading } = useVogueShowDetail(selectedShowId);

  const images = showDetail?.images || [];
  const filteredImages = imageTypeFilter === "all" ? images : images.filter(img => img.image_type === imageTypeFilter);

  const typeCounts = {};
  images.forEach(img => {
    typeCounts[img.image_type] = (typeCounts[img.image_type] || 0) + 1;
  });

  const TYPE_ORDER = ["collection", "detail", "beauty", "backstage", "atmosphere", "front_row"];

  return (
    <main className="flex-1 flex flex-col overflow-hidden bg-[var(--color-bg)]">
      {/* Sticky Header + Filters */}
      <div className="shrink-0 bg-[var(--color-bg)] border-b border-[var(--color-border)] px-8 pt-6 pb-4">
        <div className="max-w-[1200px] mx-auto">
          <h1 className="font-['Lora'] text-xl font-semibold tracking-wide mb-1">Vogue Runway</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mb-3">
            Collection + Detail imagery from Vogue Runway
            {stats && (
              <span className="ml-2 text-[var(--color-text-muted)]">
                &middot; {stats.total_shows} shows &middot; {stats.total_images?.toLocaleString()} images
              </span>
            )}
          </p>

          {/* Filters Row */}
          <div className="flex gap-3 flex-wrap items-center">
            {/* Designer Dropdown */}
            <select
              value={selectedDesigner || ""}
              onChange={(e) => {
                setSelectedDesigner(e.target.value || null);
                setSelectedType(null);
                setImageTypeFilter("all");
              }}
              className="text-xs px-3 py-2 border border-[var(--color-border)] rounded-md bg-white text-[var(--color-text)]"
            >
              <option value="" disabled>— Designer —</option>
              {designers.map(d => (
                <option key={d.slug} value={d.slug}>
                  {d.name} ({d.showCount} shows)
                </option>
              ))}
            </select>

            {/* Season Dropdown */}
            <select
              value={selectedSeason || ""}
              onChange={(e) => {
                setSelectedSeason(e.target.value || null);
                setSelectedType(null);
                setImageTypeFilter("all");
              }}
              className="text-xs px-3 py-2 border border-[var(--color-border)] rounded-md bg-white text-[var(--color-text)]"
            >
              <option value="">All Seasons</option>
              {seasons.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>

            {/* Collection Type Dropdown */}
            <select
              value={selectedType || ""}
              onChange={(e) => {
                setSelectedType(e.target.value || null);
                setImageTypeFilter("all");
              }}
              className="text-xs px-3 py-2 border border-[var(--color-border)] rounded-md bg-white text-[var(--color-text)]"
            >
              <option value="">All Types</option>
              {collectionTypes.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>

            {/* Count */}
            <div className="ml-auto text-xs text-[var(--color-text-muted)] self-center">
              {matchingShows.length} show{matchingShows.length !== 1 ? "s" : ""} matched
            </div>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        <div className="max-w-[1200px] mx-auto space-y-6">

          {/* Multiple shows matched → show list */}
          {matchingShows.length > 1 && (
            <div className="space-y-3">
              <p className="text-xs text-[var(--color-text-muted)]">
                {matchingShows.length}개 쇼가 매칭됨 — 시즌이나 타입을 선택해서 좁혀주세요, 또는 쇼를 직접 클릭하세요.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {matchingShows.map(show => (
                  <button
                    key={show.id}
                    onClick={() => {
                      setSelectedSeason(show.season);
                      setSelectedType(show.collection_type);
                    }}
                    className="text-left p-4 bg-white border border-[var(--color-border)] rounded-lg hover:shadow-md transition-shadow"
                  >
                    <p className="font-['Lora'] font-semibold text-sm">{show.show_name}</p>
                    <p className="text-xs text-[var(--color-text-secondary)] mt-1">
                      {show.city} &middot; {show.show_date}
                    </p>
                    <p className="text-xs text-[var(--color-text-muted)] mt-1">
                      {show.total_looks} looks &middot; {show.total_details} details &middot; {show.collection_type}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Single show selected → show gallery */}
          {selectedShowId && showDetail?.show && (
            <div className="space-y-4">
              {/* Show Info Bar */}
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <h2 className="font-['Lora'] text-lg font-semibold">{showDetail.show.show_name}</h2>
                  <p className="text-xs text-[var(--color-text-secondary)]">
                    {showDetail.show.city} &middot; {showDetail.show.show_date} &middot; {showDetail.show.collection_type}
                  </p>
                </div>
                <div className="text-xs text-[var(--color-text-muted)]">
                  {images.length} images
                </div>
              </div>

              {/* Image Type Filter Pills */}
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => setImageTypeFilter("all")}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                    imageTypeFilter === "all" ? "bg-gray-800 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  All ({images.length})
                </button>
                {TYPE_ORDER.filter(t => typeCounts[t]).map(type => (
                  <button
                    key={type}
                    onClick={() => setImageTypeFilter(type)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                      imageTypeFilter === type
                        ? (TYPE_COLORS[type] || "bg-gray-200 text-gray-700") + " ring-2 ring-offset-1"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                  >
                    {TYPE_LABELS[type] || type} ({typeCounts[type]})
                  </button>
                ))}
                {/* Any types not in TYPE_ORDER */}
                {Object.keys(typeCounts).filter(t => !TYPE_ORDER.includes(t)).map(type => (
                  <button
                    key={type}
                    onClick={() => setImageTypeFilter(type)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                      imageTypeFilter === type
                        ? "bg-gray-700 text-white ring-2 ring-offset-1 ring-gray-400"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                  >
                    {type} ({typeCounts[type]})
                  </button>
                ))}
              </div>

              {/* Image Grid */}
              {detailLoading ? (
                <div className="py-20 text-center text-sm text-[var(--color-text-muted)]">Loading images...</div>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
                  {filteredImages.map(img => (
                    <ImageCard key={img.id} image={img} onClick={setModalImage} />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* No shows matched */}
          {!showsLoading && matchingShows.length === 0 && (
            <div className="py-20 text-center">
              <p className="text-sm text-[var(--color-text-muted)]">
                {allShows.length === 0
                  ? "No shows collected yet. Run the Vogue Runway crawler first."
                  : "No shows match the current filters."}
              </p>
            </div>
          )}
        </div>
      </div>

      <ImageModal image={modalImage} onClose={() => setModalImage(null)} />
    </main>
  );
}
