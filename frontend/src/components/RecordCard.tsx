import { useNavigate } from "react-router-dom";
import { Trash2 } from "lucide-react";

export default function RecordCard({ record, onDelete }: any) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate("/result", { state: record })}
      className="bg-white rounded-xl shadow overflow-hidden relative group cursor-pointer hover:shadow-lg transition"
    >

      {/*  DELETE BUTTON */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete(record.id);
        }}
        className="
          absolute top-3 right-3 z-20
          bg-red-500 hover:bg-red-600 text-white
          p-2 rounded-full shadow
          opacity-0 group-hover:opacity-100
          transition
        "
      >
        <Trash2 size={14} />
      </button>

      {/* IMAGE */}
      <div className="relative">
        <img
          src={record.image_url}
          className="w-full h-44 object-cover"
        />

        {/* TYPE */}
        <span className="absolute top-2 left-2 bg-orange-500 text-white text-xs px-2 py-1 rounded">
          {record.predicted_class}
        </span>

        {/* NAME */}
        <span className="absolute top-2 right-2 bg-gray-200 text-xs px-2 py-1 rounded">
          {record.name}
        </span>

        {/* GRADE */}
        <span className="absolute bottom-2 right-2 bg-blue-500 text-white text-xs px-3 py-1 rounded-full">
          {record.grade}
        </span>
      </div>

      {/* DETAILS */}
      <div className="p-4 space-y-2">

        <div className="flex justify-between">
          <span className="font-medium">
            #{record.id.toString().slice(-3)}
          </span>

          <span className="text-green-600 font-bold">
            {record.score}/100
          </span>
        </div>

        <p className="text-sm text-gray-500">
          tenali, guntur
        </p>

        <p className="text-sm text-gray-500">
          {new Date(record.id).toDateString()}
        </p>

        <div className="flex justify-between pt-2 border-t">
          <span className="text-sm text-gray-500">
            Female • 1y 3m
          </span>

          <span className="text-xs px-2 py-1 border border-green-500 text-green-600 rounded">
            completed
          </span>
        </div>

      </div>
    </div>
  );
}