"""
Pydantic Schemas — ATC System
Request / Response models for all API endpoints
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ─── Animal ───────────────────────────────────────────────────────────────────

class AnimalCreate(BaseModel):
    tag_number: Optional[str] = None
    name: Optional[str] = None
    breed: Optional[str] = None
    age_years: Optional[float] = None
    sex: Optional[str] = "unknown"
    owner_name: Optional[str] = None
    owner_contact: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class AnimalResponse(AnimalCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# ─── Image ────────────────────────────────────────────────────────────────────

class ImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    animal_id: str
    filename: str
    filepath: str
    original_name: Optional[str] = None
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    is_processed: bool
    created_at: datetime


class UploadResponse(BaseModel):
    image_id: str
    animal_id: str
    filename: str
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    message: str = "Image uploaded successfully"


# ─── Morphometrics ────────────────────────────────────────────────────────────

class MorphometricMeasurements(BaseModel):
    body_length_px: Optional[float] = None
    height_px: Optional[float] = None
    chest_width_px: Optional[float] = None
    chest_girth_px: Optional[float] = None
    body_depth_px: Optional[float] = None
    rump_width_px: Optional[float] = None
    pixel_per_cm: Optional[float] = None
    body_length_cm: Optional[float] = None
    height_cm: Optional[float] = None
    chest_girth_cm: Optional[float] = None
    body_depth_cm: Optional[float] = None
    rump_width_cm: Optional[float] = None


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float


# ─── Classification ───────────────────────────────────────────────────────────

class ClassifyRequest(BaseModel):
    image_id: str
    animal_id: Optional[str] = None


class ComponentScores(BaseModel):
    body_length: float = Field(..., ge=0, le=100)
    height: float = Field(..., ge=0, le=100)
    chest_girth: float = Field(..., ge=0, le=100)
    rump_angle: float = Field(..., ge=0, le=100)
    rump_width: float = Field(..., ge=0, le=100)
    body_depth: float = Field(..., ge=0, le=100)
    dairy_character: float = Field(..., ge=0, le=100)
    feet_legs: float = Field(..., ge=0, le=100)
    udder: float = Field(..., ge=0, le=100)


class ATCScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    final_score: float
    grade: str
    component_scores: ComponentScores


class ClassificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    animal_id: str
    image_id: str
    predicted_class: str
    confidence: float
    detection_confidence: Optional[float] = None
    bbox: Optional[BoundingBox] = None
    measurements: Optional[MorphometricMeasurements] = None
    score: Optional[ATCScoreResponse] = None
    processing_time_ms: Optional[float] = None
    status: str
    created_at: datetime


# ─── Records ──────────────────────────────────────────────────────────────────

class RecordSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tag_number: Optional[str] = None
    name: Optional[str] = None
    breed: Optional[str] = None
    predicted_class: Optional[str] = None
    confidence: Optional[float] = None
    final_score: Optional[float] = None
    grade: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime


class PaginatedRecords(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[RecordSummary]


# ─── Reports ──────────────────────────────────────────────────────────────────

class ClassDistribution(BaseModel):
    cow: int
    buffalo: int
    unknown: int


class GradeDistribution(BaseModel):
    excellent: int
    good_plus: int
    good: int
    average: int


class ScoreTrend(BaseModel):
    date: str
    avg_score: float
    count: int


class ReportSummary(BaseModel):
    total_classifications: int
    avg_confidence: float
    avg_score: float
    class_distribution: ClassDistribution
    grade_distribution: GradeDistribution
    score_trends: List[ScoreTrend]
    top_grade_percentage: float
