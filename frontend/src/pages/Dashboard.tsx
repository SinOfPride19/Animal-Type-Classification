import { useNavigate } from "react-router-dom";
import { getRecords } from "../api";

export default function Dashboard() {
  const navigate = useNavigate();

  // get all saved records
  const records: any[] = getRecords();

  // counts
  const total = records.length;

  const cattle = records.filter((r: any) => r.predicted_class === "cattle").length;

  const buffalo = records.filter((r: any) => r.predicted_class === "buffalo").length;

  // average score
  const avg =
    records.length === 0
      ? 0
      : Math.round(
          records.reduce((sum: number, r: any) => sum + (r.score || 0), 0) /
            records.length
        );

  return (
    <div className="space-y-6">

      {/* HEADER */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Animal Type Classification</h1>
          <p className="text-gray-500 text-sm">
            AI-powered evaluation system
          </p>
        </div>

        <button
          onClick={() => navigate("/classify")}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
        >
          + New Classification
        </button>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl shadow">
          <p className="text-sm text-gray-500">Total Animals</p>
          <h2 className="text-2xl font-bold">{total}</h2>
        </div>

        <div className="bg-white p-5 rounded-xl shadow">
          <p className="text-sm text-gray-500">Cattle</p>
          <h2 className="text-2xl font-bold">{cattle}</h2>
        </div>

        <div className="bg-white p-5 rounded-xl shadow">
          <p className="text-sm text-gray-500">Buffalo</p>
          <h2 className="text-2xl font-bold">{buffalo}</h2>
        </div>

        <div className="bg-white p-5 rounded-xl shadow">
          <p className="text-sm text-gray-500">Avg Score</p>
          <h2 className="text-2xl font-bold">{avg}/100</h2>
        </div>
      </div>

      {/* ACTION CARDS */}
      <div className="grid grid-cols-3 gap-4">

        <div
          onClick={() => navigate("/classify")}
          className="bg-white p-6 rounded-xl shadow cursor-pointer hover:shadow-lg transition"
        >
          <h3 className="font-semibold">Start Classification</h3>
          <p className="text-sm text-gray-500">
            Capture & analyze animal images
          </p>
        </div>

        <div
          onClick={() => navigate("/records")}
          className="bg-white p-6 rounded-xl shadow cursor-pointer hover:shadow-lg transition"
        >
          <h3 className="font-semibold">View Records</h3>
          <p className="text-sm text-gray-500">
            Browse classified animals
          </p>
        </div>

        <div
          onClick={() => navigate("/reports")}
          className="bg-white p-6 rounded-xl shadow cursor-pointer hover:shadow-lg transition"
        >
          <h3 className="font-semibold">Reports</h3>
          <p className="text-sm text-gray-500">
            Analytics & charts
          </p>
        </div>
      </div>

      {/* RECENT */}
      <div className="bg-white p-6 rounded-xl shadow">
        <h2 className="font-semibold mb-4">Recent Classifications</h2>

        {records.length === 0 ? (
          <p className="text-gray-500">No classifications yet</p>
        ) : (
          <div className="flex gap-4 overflow-x-auto">
            {records.slice(0, 3).map((r: any) => (
              <div key={r.id} className="min-w-[200px]">
                <img
                  src={r.image_url}
                  className="h-32 w-full object-cover rounded-lg"
                />
                <p className="mt-2 font-medium">{r.name}</p>
                <p className="text-sm text-green-600">{r.score}/100</p>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}