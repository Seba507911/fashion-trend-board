import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ProductBoard from "./components/ProductBoard";
import TrendAnalysis from "./pages/TrendAnalysis";
import GraphView from "./pages/GraphView";
import Runway from "./pages/Runway";

export default function App() {
  const [selectedBrand, setSelectedBrand] = useState(null);

  return (
    <BrowserRouter>
      <div className="flex min-h-screen">
        <Sidebar selectedBrand={selectedBrand} onBrandSelect={setSelectedBrand} />
        <Routes>
          <Route path="/" element={<ProductBoard selectedBrand={selectedBrand} />} />
          <Route path="/trend" element={<TrendAnalysis />} />
          <Route path="/graph" element={<GraphView />} />
          <Route path="/runway" element={<Runway />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
