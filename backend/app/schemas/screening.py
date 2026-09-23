from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScreeningCreate(BaseModel):
    patient_id: int
    eye_side: Optional[str] = "unknown"
    mode: Optional[str] = "demo"


class ScreeningResponse(BaseModel):
    id: int
    patient_id: int
    status: str
    mode: str
    eye_side: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class QualityResult(BaseModel):
    status: str
    score: Optional[float]
    blur_score: Optional[float]
    brightness_score: Optional[float]
    contrast_score: Optional[float]
    retinal_visibility: Optional[str]
    reasons: Optional[List[str]]


class ProbabilityDistribution(BaseModel):
    grade_0: float
    grade_1: float
    grade_2: float
    grade_3: float
    grade_4: float


class ClassificationResult(BaseModel):
    model_name: str
    model_version: str
    predicted_grade: int
    predicted_label: str
    probabilities: ProbabilityDistribution
    confidence: float
    calibration_status: str
    mode: str


class LesionResult(BaseModel):
    lesion_type: str
    status: str
    confidence: Optional[float]


class ExplanationResult(BaseModel):
    explanation_type: str
    image_url: Optional[str]
    available: bool


class DecisionResult(BaseModel):
    decision: str  # clear | refer | escalate
    reason: str
    evidence_status: str


class ScreeningAnalysisResult(BaseModel):
    screening_id: int
    mode: str
    quality: QualityResult
    classification: Optional[ClassificationResult]
    explanation: Optional[ExplanationResult]
    lesions: Optional[List[LesionResult]]
    decision: DecisionResult
    is_demo: bool


class ReviewCreate(BaseModel):
    clinical_assessment: Optional[str] = None
    final_recommendation: Optional[str] = None
    notes: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    screening_id: int
    clinical_assessment: Optional[str]
    final_recommendation: Optional[str]
    notes: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
