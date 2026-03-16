import KeywordCard from "./KeywordCard";

export default function KeywordGrid({ keywords, selectedId, onSelect }) {
  return (
    <div className="grid gap-3" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))" }}>
      {keywords.map((kw) => (
        <KeywordCard
          key={kw.id}
          data={kw}
          isSelected={selectedId === kw.id}
          onClick={() => onSelect(selectedId === kw.id ? null : kw.id)}
        />
      ))}
    </div>
  );
}
