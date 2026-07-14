import { getRecords } from "../api";
import {
  PieChart, Pie, Cell,
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts";

export default function ReportsPage() {
  const records: any[] = getRecords();

  const cattle = records.filter((r: any) => r.predicted_class === "cattle").length;
  const buffalo = records.filter((r: any) => r.predicted_class === "buffalo").length;

  const avg =
    records.length === 0
      ? 0
      : Math.round(records.reduce((a: number, b: any) => a + b.score, 0) / records.length);

  // PIE DATA
  const pieData = [
    { name: "Cattle", value: cattle },
    { name: "Buffalo", value: buffalo }
  ];

  // BAR DATA
  const barData = records.map((r: any, i: number) => ({
    name: `#${i + 1}`,
    score: r.score
  }));

  return (
    <div className="space-y-6">

      <h1 className="text-2xl font-bold">Reports & Analytics</h1>

      {/* STATS */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-green-500 text-white p-5 rounded-xl">Total {records.length}</div>
        <div className="bg-blue-500 text-white p-5 rounded-xl">Cattle {cattle}</div>
        <div className="bg-pink-500 text-white p-5 rounded-xl">Buffalo {buffalo}</div>
        <div className="bg-orange-500 text-white p-5 rounded-xl">Avg {avg}</div>
      </div>

      {/* CHARTS */}
      <div className="grid grid-cols-2 gap-6">

        {/* PIE */}
        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="mb-4 font-semibold">Animal Distribution</h2>

          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} dataKey="value" outerRadius={80}>
                <Cell fill="#3B82F6" />
                <Cell fill="#EC4899" />
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* BAR */}
        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="mb-4 font-semibold">Scores</h2>

          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={barData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="score" />
            </BarChart>
          </ResponsiveContainer>
        </div>

      </div>
    </div>
  );
}