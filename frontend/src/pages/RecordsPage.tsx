import { useNavigate } from "react-router-dom"
import { getRecords } from "../api"
import { Search, Grid, List } from "lucide-react"
import { useState } from "react"
import RecordCard from "../components/RecordCard"

export default function RecordsPage() {
  const navigate = useNavigate()
  const [records, setRecords] = useState(getRecords())
  const [search, setSearch] = useState("")
  const [typeFilter, setTypeFilter] = useState("All Types")
  const [gradeFilter, setGradeFilter] = useState("All Grades")

  function deleteRecord(id: number) {
    const updated = records.filter((r: any) => r.id !== id)
    localStorage.setItem("records", JSON.stringify(updated))
    setRecords(updated)
  }

  //  SEARCH + FILTER
  const filteredRecords = records.filter((r: any) => {
    const matchesSearch =
      r.name?.toLowerCase().includes(search.toLowerCase()) ||
      r.id.toString().includes(search)

    const matchesType =
      typeFilter === "All Types" ||
      r.predicted_class.toLowerCase() === typeFilter.toLowerCase()

    const matchesGrade =
      gradeFilter === "All Grades" ||
      r.grade === gradeFilter

    return matchesSearch && matchesType && matchesGrade
  })

  return (
    <div className="space-y-6">

      {/* BACK */}
      <button
        onClick={() => navigate("/")}
        className="text-sm text-gray-600"
      >
        ← Back to Dashboard
      </button>

      {/* HEADER */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Animal Records</h1>
          <p className="text-gray-500 text-sm">
            {filteredRecords.length} animals found
          </p>
        </div>

        <button
          onClick={() => navigate("/classify")}
          className="bg-green-600 text-white px-5 py-2 rounded-lg hover:bg-green-700 transition"
        >
          + New Classification
        </button>
      </div>

      {/* FILTER BAR */}
      <div className="bg-white rounded-xl shadow p-4 flex items-center gap-4">

        {/* SEARCH */}
        <div className="flex items-center gap-2 border px-3 py-2 rounded w-full">
          <Search size={16} />
          <input
            placeholder="Search by name or ID..."
            className="outline-none w-full"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* TYPE */}
        <select
          className="border px-3 py-2 rounded"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
        >
          <option>All Types</option>
          <option>Cattle</option>
          <option>Buffalo</option>
        </select>

        {/* GRADE */}
        <select
          className="border px-3 py-2 rounded"
          value={gradeFilter}
          onChange={(e) => setGradeFilter(e.target.value)}
        >
          <option>All Grades</option>
          <option>Excellent</option>
          <option>Good</option>
          <option>Average</option>
          <option>Poor</option>
        </select>

        {/* VIEW */}
        <button className="bg-green-600 text-white p-2 rounded">
          <Grid size={16} />
        </button>

        <button className="border p-2 rounded">
          <List size={16} />
        </button>
      </div>

      {/* GRID USING RECORD CARD */}
      <div className="grid grid-cols-3 gap-6">
        {filteredRecords.map((r: any) => (
          <RecordCard
            key={r.id}
            record={r}
            onDelete={deleteRecord}
          />
        ))}
      </div>

    </div>
  )
}