from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.sql import func
from app.database.base import Base


class Screening(Base):
    __tablename__ = "screenings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="created")
    mode = Column(String(20), nullable=False, default="demo")  # live | demo
    eye_side = Column(String(10), nullable=True)  # left | right | unknown
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class UploadedImage(Base):
    __tablename__ = "uploaded_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    screening_id = Column(Integer, ForeignKey("screenings.id"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class ImageQualityResult(Base):
    __tablename__ = "image_quality_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    screening_id = Column(Integer, ForeignKey("screenings.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # good | poor
    score = Column(Float, nullable=True)
    blur_score = Column(Float, nullable=True)
    brightness_score = Column(Float, nullable=True)
    contrast_score = Column(Float, nullable=True)
    retinal_visibility = Column(String(20), nullable=True)
    reasons = Column(JSON, nullable=True)  # list of reason strings
    created_at = Column(DateTime, default=func.now(), nullable=False)


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    screening_id = Column(Integer, ForeignKey("screenings.id"), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    predicted_grade = Column(Integer, nullable=False)
    predicted_label = Column(String(100), nullable=False)
    probabilities = Column(JSON, nullable=False)  # {0:p0, 1:p1, ...}
    confidence = Column(Float, nullable=False)
    calibration_status = Column(String(50), nullable=False, default="unavailable")
    mode = Column(String(20), nullable=False, default="demo")
    created_at = Column(DateTime, default=func.now(), nullable=False)


class LesionFinding(Base):
    __tablename__ = "lesion_findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    screening_id = Column(Integer, ForeignKey("screenings.id"), nullable=False, index=True)
    lesion_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # detected | not_detected | insufficient_evidence | not_configured
    confidence = Column(Float, nullable=True)
    overlay_path = Column(String(500), nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class Explanation(Base):
    __tablename__ = "explanations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    screening_id = Column(Integer, ForeignKey("screenings.id"), nullable=False, index=True)
    explanation_type = Column(String(50), nullable=False, default="gradcam")
    image_path = Column(String(500), nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class DecisionRecord(Base):
    __tablename__ = "decision_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    screening_id = Column(Integer, ForeignKey("screenings.id"), nullable=False, index=True)
    decision = Column(String(20), nullable=False)  # clear | refer | escalate
    reason = Column(Text, nullable=False)
    evidence_status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class ClinicianReview(Base):
    __tablename__ = "clinician_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    screening_id = Column(Integer, ForeignKey("screenings.id"), nullable=False, index=True)
    clinician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    clinical_assessment = Column(Text, nullable=True)
    final_recommendation = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
