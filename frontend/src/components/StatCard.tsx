export default function StatCard({ title, value, color }: any) {
  return (
    <div className={`p-5 rounded-xl shadow-sm bg-white`}>
      <p className="text-sm text-gray-500">{title}</p>
      <h2 className="text-2xl font-bold">{value}</h2>
    </div>
  );
}