import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import ClassifyPage from "./pages/ClassifyPage";
import RecordsPage from "./pages/RecordsPage";
import ReportsPage from "./pages/ReportsPage";
import Result from "./pages/Result";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex">
        <Sidebar />

        <div className="flex-1 bg-gray-100 min-h-screen p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/classify" element={<ClassifyPage />} />
            <Route path="/records" element={<RecordsPage />} />
            <Route path="/reports" element={<ReportsPage />} />

            {/* ✅ FIX — THIS WAS WRONG BEFORE */}
            <Route path="/result" element={<Result />} />

          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}