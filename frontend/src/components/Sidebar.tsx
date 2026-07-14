import { NavLink } from "react-router-dom";
import { LayoutDashboard, Camera, List, BarChart3 } from "lucide-react";

export default function Sidebar() {
  const linkClass = ({ isActive }: any) =>
    `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition ${
      isActive
        ? "bg-green-600 text-white"
        : "text-gray-600 hover:bg-gray-100"
    }`;

  return (
    <div className="w-64 h-screen bg-white border-r flex flex-col p-4">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-green-600 text-white p-2 rounded-lg">📷</div>
        <div>
          <h1 className="font-bold text-lg mb-6">ATC System</h1>
        </div>
      </div>

      <nav className="flex flex-col gap-2">
        <NavLink to="/" className={linkClass}>
          <LayoutDashboard size={18} /> Dashboard
        </NavLink>

        <NavLink to="/classify" className={linkClass}>
          <Camera size={18} /> New Classification
        </NavLink>

        <NavLink to="/records" className={linkClass}>
          <List size={18} /> Records
        </NavLink>

        <NavLink to="/reports" className={linkClass}>
          <BarChart3 size={18} /> Reports
        </NavLink>
      </nav>
    </div>
  );
}