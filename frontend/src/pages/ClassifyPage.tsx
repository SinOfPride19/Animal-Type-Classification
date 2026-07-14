import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import {
  ChevronRight, ChevronLeft, Loader2
} from 'lucide-react'
import { classifyAnimal, saveRecord } from '../api'
import { useNavigate } from "react-router-dom"

export default function ClassifyPage() {
  const [step, setStep] = useState(1)
  const [animalInfo, setAnimalInfo] = useState<any>({})
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [classifying, setClassifying] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const navigate = useNavigate()

  function toBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = reject
    })
  }

  function handleInfoChange(e: any) {
    setAnimalInfo({ ...animalInfo, [e.target.name]: e.target.value })
  }

  const onDrop = useCallback((accepted: File[]) => {
    const f = accepted[0]
    if (!f) return

    setFile(f)
    setPreviewUrl(URL.createObjectURL(f))
    toast.success("Image selected")
    setStep(3)
  }, [])

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png'] },
    maxFiles: 1
  })

  async function handleClassify() {
    if (!file) {
      toast.error("Upload image first")
      return
    }

    setClassifying(true)

    try {
      const res = await classifyAnimal(file)

// 🔥 HANDLE BACKEND ERROR FIRST
if (res?.error) {
  toast.error(res.message || "Invalid image. Upload cow or buffalo")
  setClassifying(false)
  return
}

// ❌ EXTRA SAFETY CHECK (keep this)
if (!res?.class || (res.class !== "cow" && res.class !== "buffalo")) {
  toast.error("❌ Image mismatch. Upload cow or buffalo")
  setClassifying(false)
  return
}

      const base64 = await toBase64(file)

      const predicted =
        res.class === "cow" ? "cattle" : "buffalo"

      const record = {
        id: Date.now(),
        name: animalInfo?.breed || "Animal",
        predicted_class: predicted,
        score: res?.score ?? 0,
        grade: res?.grade ?? "Average",
        confidence: res?.confidence ?? 85,
        image_url: base64,
        measurements: {
          body_length_cm: res?.measurements?.body_length ?? 0,
          height_cm: res?.measurements?.height ?? 0,
          chest_girth_cm: res?.measurements?.chest_girth ?? 0,
          chest_width_cm: res?.measurements?.chest_width ?? 0
        },
        components: res?.components ?? {}
      }

      saveRecord(record)
      navigate("/result", { state: record })

      toast.success("AI Analysis Complete")

    } catch (e) {
      console.error(e)
      setError("Backend error")
      toast.error("Classification failed")
    } finally {
      setClassifying(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">

      {/* STEP 1 */}
      {step === 1 && (
        <div className="bg-white p-6 rounded-xl shadow space-y-6">

          <h2 className="text-xl font-bold">Step 1: Animal Information</h2>

          <div className="grid grid-cols-2 gap-4">

            <input name="tag" placeholder="Tag Number" onChange={handleInfoChange} className="border p-2 rounded" />

            <select name="type" onChange={handleInfoChange} className="border p-2 rounded">
              <option>Cattle</option>
              <option>Buffalo</option>
            </select>

            <select name="breed" onChange={handleInfoChange} className="border p-2 rounded">
              <option>Select Breed</option>

              {/* CATTLE */}
              <option>Sahiwal</option>
              <option>Gir</option>
              <option>Rathi</option>
              <option>Red Sindhi</option>
              <option>Tharparkar</option>
              <option>Kankrej</option>
              <option>Hariana</option>
              <option>Ongole</option>
              <option>Deoni</option>
              <option>Hallikar</option>
              <option>Amritmahal</option>
              <option>Khillari</option>
              <option>Kangayam</option>
              <option>Vechur</option>

              {/* BUFFALO */}
              <option>Murrah</option>
              <option>Jaffarabadi</option>
              <option>Surti</option>
              <option>Mehsana</option>
              <option>Bhadawari</option>
              <option>Nagpuri</option>
              <option>Pandharpuri</option>
              <option>Toda</option>
              <option>Kundi</option>
            </select>

            <select name="gender" onChange={handleInfoChange} className="border p-2 rounded">
              <option>Female</option>
              <option>Male</option>
            </select>

            <input name="age" placeholder="Age (months)" type="number" onChange={handleInfoChange} className="border p-2 rounded" />
            <input name="owner" placeholder="Owner Name" onChange={handleInfoChange} className="border p-2 rounded" />
            <input name="phone" placeholder="Phone" onChange={handleInfoChange} className="border p-2 rounded" />
            <input name="location" placeholder="Village/Farm Location" onChange={handleInfoChange} className="border p-2 rounded" />
            <input name="district" placeholder="District" onChange={handleInfoChange} className="border p-2 rounded" />

            <select name="state" onChange={handleInfoChange} className="border p-2 rounded">
              <option>Select State</option>
              <option>Andhra Pradesh</option>
              <option>Arunachal Pradesh</option>
              <option>Assam</option>
              <option>Bihar</option>
              <option>Chhattisgarh</option>
              <option>Goa</option>
              <option>Gujarat</option>
              <option>Haryana</option>
              <option>Himachal Pradesh</option>
              <option>Jharkhand</option>
              <option>Karnataka</option>
              <option>Kerala</option>
              <option>Madhya Pradesh</option>
              <option>Maharashtra</option>
              <option>Manipur</option>
              <option>Meghalaya</option>
              <option>Mizoram</option>
              <option>Nagaland</option>
              <option>Odisha</option>
              <option>Punjab</option>
              <option>Rajasthan</option>
              <option>Sikkim</option>
              <option>Tamil Nadu</option>
              <option>Telangana</option>
              <option>Tripura</option>
              <option>Uttar Pradesh</option>
              <option>Uttarakhand</option>
              <option>West Bengal</option>
            </select>

          </div>

          <textarea
            name="notes"
            placeholder="Additional Notes"
            onChange={handleInfoChange}
            className="border p-2 w-full rounded"
          />

          <div className="flex justify-end">
            <button
              onClick={() => setStep(2)}
              className="bg-green-600 text-white px-6 py-2 rounded"
            >
              Next →
            </button>
          </div>

        </div>
      )}

      {/* STEP 2 */}
      {step === 2 && (
        <div className="bg-white p-6 rounded-xl shadow space-y-4">
          <h2 className="text-xl font-bold">Upload Image</h2>

          <div {...getRootProps()} className="border-2 border-dashed p-10 text-center rounded cursor-pointer">
            <input {...getInputProps()} />
            {previewUrl ? (
              <img src={previewUrl} className="max-h-40 mx-auto" />
            ) : (
              <p>Click or Drag Image</p>
            )}
          </div>

          <button onClick={() => setStep(1)}>
            <ChevronLeft /> Back
          </button>
        </div>
      )}

      {/* STEP 3 */}
      {step === 3 && (
        <div className="bg-white p-6 rounded-xl shadow space-y-6">

          <h2 className="text-xl font-bold text-center">Capture Image</h2>

          {previewUrl && (
            <div className="flex flex-col items-center space-y-4">
              <img src={previewUrl} className="max-h-56 rounded-lg" />

              {classifying ? (
                <Loader2 className="animate-spin" />
              ) : (
                <button
                  onClick={handleClassify}
                  className="bg-green-600 text-white px-6 py-2 rounded"
                >
                  Run AI
                </button>
              )}
            </div>
          )}

          <button
            onClick={() => {
              setFile(null)
              setPreviewUrl(null)
              setStep(2)
            }}
            className="bg-blue-500 text-white px-4 py-1 rounded text-sm"
          >
            Retake
          </button>

        </div>
      )}

      {error && <p className="text-red-500">{error}</p>}
    </div>
  )
}