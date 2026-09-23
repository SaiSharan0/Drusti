import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env before importing anything else
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.database.database import engine
from app.database.base import Base

# Import all models so they are registered with Base.metadata
from app.models.user import User
from app.models.patient import Patient
from app.models.screening import (
    Screening, UploadedImage, ImageQualityResult, ModelPrediction,
    LesionFinding, Explanation, DecisionRecord, ClinicianReview,
)
from app.models.facility import Facility
from app.models.audit import AuditLog

# Import routers
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.patients import router as patients_router
from app.api.screenings import router as screenings_router
from app.api.facilities import router as facilities_router
from app.api.analytics import router as analytics_router
from app.api.pdf_export import router as pdf_export_router

setup_logging()
settings = get_settings()

app = FastAPI(
    title="Drusti API",
    description="AI-Assisted Diabetic Retinopathy Screening System",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Mount static files for uploaded images
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/data/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Seed data on startup
from app.database.database import SessionLocal
from app.database.seed import run_seed

@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Pre-load AI model at startup so it's ready on first request
    from app.ml.classifier import ModelManager
    import logging
    logger = logging.getLogger(__name__)
    manager = ModelManager.get_instance()
    if manager.is_loaded:
        logger.info("DRUSTI AI MODEL: READY (ResNet-50, 5 classes, CPU)")
    else:
        logger.warning(f"DRUSTI AI MODEL: NOT READY — {manager.error}")

# Register routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(patients_router)
app.include_router(screenings_router)
app.include_router(facilities_router)
app.include_router(analytics_router)
app.include_router(pdf_export_router)


from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.database import get_db

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    from app.ml.classifier import ModelManager
    manager = ModelManager.get_instance()

    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    ai_ready = manager.is_loaded
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "ai_model": "ready" if ai_ready else "not_ready",
        "model": "ResNet-50" if ai_ready else None,
        "classes": 5 if ai_ready else None,
        "version": "1.0.0",
        "error": manager.error if not ai_ready else None,
    }


@app.get("/api/health/ai")
def health_ai():
    """Dedicated AI model health check for development diagnostics."""
    from app.ml.classifier import ModelManager
    manager = ModelManager.get_instance()
    return {
        "ai_model": "ready" if manager.is_loaded else "not_ready",
        "model": "ResNet-50",
        "classes": 5,
        "checkpoint": settings.MODEL_CLASSIFIER_PATH,
        "checkpoint_exists": os.path.exists(settings.MODEL_CLASSIFIER_PATH),
        "error": manager.error,
    }


@app.get("/api/settings/status")
def system_status():
    classifier_exists = os.path.exists(settings.MODEL_CLASSIFIER_PATH)
    segmentation_exists = os.path.exists(settings.MODEL_SEGMENTATION_PATH)
    calibration_exists = os.path.exists(settings.CALIBRATION_PATH)
    return {
        "success": True,
        "data": {
            "mode": settings.DRUSTI_MODE,
            "classifier_configured": classifier_exists,
            "segmentation_configured": segmentation_exists,
            "calibration_configured": calibration_exists,
            "database": "connected",
            "version": "1.0.0",
        },
    }
