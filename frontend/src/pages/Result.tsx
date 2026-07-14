import { useLocation } from "react-router-dom"
import { getRecords } from "../api"

export default function Result() {
  const location = useLocation()

  console.log("RESULT PAGE STATE:", location.state)

  let data = location.state

  //  fallback if state lost
  if (!data) {
    const records = getRecords()
    data = records.length > 0 ? records[0] : null
  }

  if (!data) {
    return (
      <div className="p-10 text-center text-red-500">
         No data received
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">

      {/* TOP CARD */}
      <div className="bg-green-50 border border-green-200 p-6 rounded-xl flex gap-4 items-center">

        <img
          src={data.image_url}
          className="w-32 h-24 object-cover rounded"
        />

        <div className="flex-1">
          <p className="text-sm text-gray-500">Tag: {data.id}</p>

          <h2 className="text-2xl font-bold capitalize">
            {data.name}
          </h2>
        </div>

        <div className="text-right">
          <p className="text-green-600 text-3xl font-bold">
            {data.score}/100
          </p>
          <p className="text-blue-500">{data.grade}</p>
        </div>
      </div>

      {/* MEASUREMENTS */}
      <div className="bg-white p-6 rounded-xl shadow">
        <h3 className="font-semibold mb-3">Body Measurements</h3>

        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-100 p-3 rounded">Length: {data.measurements?.body_length_cm}</div>
          <div className="bg-gray-100 p-3 rounded">Height: {data.measurements?.height_cm}</div>
          <div className="bg-gray-100 p-3 rounded">Chest: {data.measurements?.chest_girth_cm}</div>
          <div className="bg-gray-100 p-3 rounded">Width: {data.measurements?.chest_width_cm}</div>
        </div>
      </div>

    </div>
  )
}