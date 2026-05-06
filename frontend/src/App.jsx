import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ProductBoard from "./components/ProductBoard";
import TrendAnalysis from "./pages/TrendAnalysis";
import GraphView from "./pages/GraphView";
import Runway from "./pages/Runway";
import TrendFlow from "./pages/TrendFlow";
import TrendFlowArchive from "./pages/TrendFlowArchive";
import TrendFlowCheck from "./pages/TrendFlowCheck";
import VlmViewer from "./pages/VlmViewer";
import ProjectBriefing from "./pages/ProjectBriefing";
import ExpertReview from "./pages/ExpertReview";
import VogueRunway from "./pages/VogueRunway";
import RunwayUnified from "./pages/RunwayUnified";
import MusinsaBoard from "./pages/MusinsaBoard";
import KeyTrend from "./pages/KeyTrend";
import VectorExplorer from "./pages/VectorExplorer";

export default function App() {
  const [selectedBrand, setSelectedBrand] = useState(null);

  return (
    <BrowserRouter>
      <div className="flex min-h-screen">
        <Sidebar selectedBrand={selectedBrand} onBrandSelect={setSelectedBrand} />
        <Routes>
          {/* Main */}
          <Route path="/" element={<ProjectBriefing />} />
          <Route path="/flow" element={<TrendFlow />} />
          <Route path="/key-trend" element={<KeyTrend />} />
          <Route path="/expert" element={<ExpertReview />} />
          <Route path="/runway" element={<RunwayUnified />} />
          <Route path="/market" element={<ProductBoard selectedBrand={selectedBrand} />} />

          {/* ETC */}
          <Route path="/musinsa" element={<MusinsaBoard />} />
          <Route path="/vectors" element={<VectorExplorer />} />
          <Route path="/trend" element={<TrendAnalysis />} />
          <Route path="/graph" element={<GraphView />} />

          {/* Archive — 기존 페이지를 그대로 유지하되 경로만 변경 */}
          <Route path="/archive/flow" element={<TrendFlowArchive />} />
          <Route path="/archive/flow-check" element={<TrendFlowCheck />} />
          <Route path="/archive/runway-tagwalk" element={<Runway />} />
          <Route path="/archive/vogue" element={<VogueRunway />} />
          <Route path="/archive/vlm" element={<VlmViewer />} />

          {/* Legacy URLs redirect (backwards compat) */}
          <Route path="/flow-check" element={<TrendFlowCheck />} />
          <Route path="/vlm" element={<VlmViewer />} />
          <Route path="/vogue" element={<VogueRunway />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
