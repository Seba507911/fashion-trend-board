import { useState } from "react";
import Runway from "./Runway";
import VogueRunway from "./VogueRunway";
import VlmViewer from "./VlmViewer";

const TABS = [
  { id: "tagwalk", label: "TagWalk", desc: "13,882 looks · 40 designers" },
  { id: "vogue", label: "Vogue Runway", desc: "47,519 images · 317 shows" },
  { id: "vlm", label: "VLM Analysis", desc: "10,094 labels · AI vision" },
];

export default function RunwayUnified() {
  const [activeTab, setActiveTab] = useState("tagwalk");

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-[var(--color-bg)]">
      {/* Tab Bar */}
      <div className="shrink-0 bg-[var(--color-bg)] border-b border-[var(--color-border)] px-8 pt-6 pb-0">
        <div className="max-w-[1200px] mx-auto">
          <h1 className="font-['Lora'] text-xl font-semibold tracking-wide mb-1">Runway</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mb-4">
            Collection looks from major fashion weeks — multi-source view
          </p>
          <div className="flex gap-0">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-5 py-3 text-sm border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? "border-[var(--color-primary)] text-[var(--color-primary)] font-semibold"
                    : "border-transparent text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] hover:border-[var(--color-border)]"
                }`}
              >
                <span>{tab.label}</span>
                <span className="ml-2 text-[10px] opacity-60">{tab.desc}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "tagwalk" && <Runway />}
        {activeTab === "vogue" && <VogueRunway />}
        {activeTab === "vlm" && <VlmViewer />}
      </div>
    </div>
  );
}
