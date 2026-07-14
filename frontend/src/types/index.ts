// ATC System — Shared TypeScript Types

export interface Animal {
  id: string
  tag_number?: string
  name?: string
  breed?: string
  age_years?: number
  sex?: string
  owner_name?: string
  owner_contact?: string
  location?: string
  notes?: string
  created_at: string
}

export interface BoundingBox {
  x1: number; y1: number; x2: number; y2: number; confidence: number
}

export interface MorphometricMeasurements {
  body_length_px?: number; height_px?: number
  chest_width_px?: number; chest_girth_px?: number
  body_depth_px?: number;  rump_width_px?: number
  pixel_per_cm?: number
  body_length_cm?: number; height_cm?: number
  chest_girth_cm?: number; body_depth_cm?: number
  rump_width_cm?: number
}

export interface ComponentScores {
  body_length: number; height: number; chest_girth: number
  rump_angle: number;  rump_width: number; body_depth: number
  dairy_character: number; feet_legs: number; udder: number
}

export type GradeType = 'Excellent' | 'Good Plus' | 'Good' | 'Average'

export interface ATCScore {
  id: string; final_score: number; grade: GradeType
  component_scores: ComponentScores
}

export interface Classification {
  id: string; animal_id: string; image_id: string
  predicted_class: 'cow' | 'buffalo' | 'unknown'
  confidence: number; detection_confidence?: number
  bbox?: BoundingBox
  measurements?: MorphometricMeasurements
  score?: ATCScore
  processing_time_ms?: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
}

export interface RecordSummary {
  id: string; tag_number?: string; name?: string; breed?: string
  predicted_class?: string; confidence?: number
  final_score?: number; grade?: GradeType; image_url?: string
  created_at: string
}

export interface PaginatedRecords {
  total: number; page: number; page_size: number
  items: RecordSummary[]
}

export interface ClassDistribution { cow: number; buffalo: number; unknown: number }
export interface GradeDistribution { excellent: number; good_plus: number; good: number; average: number }
export interface ScoreTrend { date: string; avg_score: number; count: number }

export interface ReportSummary {
  total_classifications: number; avg_confidence: number; avg_score: number
  class_distribution: ClassDistribution; grade_distribution: GradeDistribution
  score_trends: ScoreTrend[]; top_grade_percentage: number
}

export interface UploadResponse {
  image_id: string; animal_id: string; filename: string
  url: string; width?: number; height?: number; message: string
}

// Classification wizard state
export interface WizardState {
  step: number
  animalInfo: Partial<Animal>
  imageId?: string
  animalId?: string
  imageUrl?: string
  classificationResult?: Classification
}
