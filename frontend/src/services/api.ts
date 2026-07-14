import axios, { AxiosError } from 'axios'
import type {
  UploadResponse, Classification, PaginatedRecords, ReportSummary
} from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120_000,
  headers: { 'Content-Type': 'application/json' },
})

// Response interceptor for unified error handling
api.interceptors.response.use(
  res => res,
  (err: AxiosError<{ detail: string }>) => {
    const msg = err.response?.data?.detail || err.message || 'Unknown error'
    return Promise.reject(new Error(msg))
  }
)

// ── Upload ────────────────────────────────────────────────────────────────────
export async function uploadImage(
  file: File,
  meta: { tag_number?: string; animal_name?: string; breed?: string; animal_id?: string }
): Promise<UploadResponse> {
  const form = new FormData()
  form.append('file', file)
  if (meta.tag_number)   form.append('tag_number', meta.tag_number)
  if (meta.animal_name)  form.append('animal_name', meta.animal_name)
  if (meta.breed)        form.append('breed', meta.breed)
  if (meta.animal_id)    form.append('animal_id', meta.animal_id)

  const { data } = await api.post<UploadResponse>('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

// ── Classify ──────────────────────────────────────────────────────────────────
export async function classifyImage(imageId: string, animalId?: string): Promise<Classification> {
  const { data } = await api.post<Classification>('/classify', {
    image_id: imageId,
    animal_id: animalId,
  })
  return data
}

// ── Records ───────────────────────────────────────────────────────────────────
export async function getRecords(params: {
  page?: number; page_size?: number; animal_class?: string; grade?: string
} = {}): Promise<PaginatedRecords> {
  const { data } = await api.get<PaginatedRecords>('/records', { params })
  return data
}

export async function getRecordDetail(id: string) {
  const { data } = await api.get(`/records/${id}`)
  return data
}

// ── Reports ───────────────────────────────────────────────────────────────────
export async function getReports(): Promise<ReportSummary> {
  const { data } = await api.get<ReportSummary>('/reports')
  return data
}

// ── Health ────────────────────────────────────────────────────────────────────
export async function getHealth() {
  const { data } = await axios.get('/api/health')
  return data
}

export async function getDashboard() {
  const res = await fetch("http://127.0.0.1:8000/dashboard");
  return res.json();
}