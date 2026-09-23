import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from PIL import Image

from app.database.database import get_db
from app.core.config import get_settings
from app.models.patient import Patient
from app.models.screening import (
    Screening, UploadedImage, ImageQualityResult,
    ModelPrediction, LesionFinding, Explanation, DecisionRecord, ClinicianReview,
)
from app.schemas.screening import ScreeningCreate, ReviewCreate

settings = get_settings()
router = APIRouter(prefix="/api/screenings", tags=["screenings"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@router.post("")
def create_screening(req: ScreeningCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == req.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    screening = Screening(
        patient_id=req.patient_id,
        eye_side=req.eye_side or "unknown",
        status="created",
        mode="live",
        started_at=datetime.utcnow(),
    )
    db.add(screening)
    db.commit()
    db.refresh(screening)
    return {"success": True, "data": {"id": screening.id, "status": screening.status, "mode": screening.mode}}


@router.post("/{screening_id}/upload")
async def upload_image(screening_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    stored_name = f"screening_{screening_id}_{uuid.uuid4().hex[:8]}{ext}"
    stored_path = os.path.join(settings.UPLOAD_DIR, stored_name)
    with open(stored_path, "wb") as f:
        f.write(content)

    try:
        img = Image.open(stored_path)
        w, h = img.size
    except Exception:
        os.remove(stored_path)
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file")

    # Remove any previous image for this screening
    old_img = db.query(UploadedImage).filter(UploadedImage.screening_id == screening_id).first()
    if old_img:
        if os.path.exists(old_img.storage_path):
            try:
                os.remove(old_img.storage_path)
            except Exception:
                pass
        db.delete(old_img)

    uploaded = UploadedImage(
        screening_id=screening_id,
        original_filename=file.filename or "unknown",
        storage_path=stored_path,
        mime_type=file.content_type,
        width=w, height=h,
        file_size=len(content),
    )
    db.add(uploaded)
    screening.status = "uploaded"
    db.commit()
    db.refresh(uploaded)

    return {"success": True, "data": {
        "id": uploaded.id, "width": w, "height": h,
        "file_size": len(content), "filename": file.filename,
        "image_url": f"/api/screenings/{screening_id}/image",
    }}


@router.get("/{screening_id}/image")
def get_image(screening_id: int, db: Session = Depends(get_db)):
    img = db.query(UploadedImage).filter(UploadedImage.screening_id == screening_id).first()
    if not img or not os.path.exists(img.storage_path):
        raise HTTPException(status_code=404, detail="Image not found")
    from fastapi.responses import FileResponse
    return FileResponse(img.storage_path, media_type=img.mime_type or "image/jpeg")


@router.get("/{screening_id}/gradcam")
def get_gradcam(screening_id: int, db: Session = Depends(get_db)):
    explanation = db.query(Explanation).filter(Explanation.screening_id == screening_id).first()
    if not explanation or not explanation.image_path or not os.path.exists(explanation.image_path):
        raise HTTPException(status_code=404, detail="Grad-CAM image not found")
    from fastapi.responses import FileResponse
    return FileResponse(explanation.image_path, media_type="image/png")


@router.get("/{screening_id}/gradcam")
def get_gradcam(screening_id: int, db: Session = Depends(get_db)):
    explanation = db.query(Explanation).filter(Explanation.screening_id == screening_id).first()
    if not explanation or not explanation.image_path or not os.path.exists(explanation.image_path):
        raise HTTPException(status_code=404, detail="Grad-CAM image not found")
    from fastapi.responses import FileResponse
    return FileResponse(explanation.image_path, media_type="image/png")


@router.post("/{screening_id}/analyze")
def analyze(screening_id: int, db: Session = Depends(get_db)):
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found")

    img_rec = db.query(UploadedImage).filter(UploadedImage.screening_id == screening_id).first()
    if not img_rec or not os.path.exists(img_rec.storage_path):
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error_code": "NO_IMAGE", "message": "No image uploaded for this screening."}
        )

    try:
        image = Image.open(img_rec.storage_path).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error_code": "INVALID_IMAGE", "message": "Uploaded image is corrupted or unreadable."}
        )

    screening.status = "analyzing"
    db.commit()

    try:
        from app.ml.classifier import LiveClassifier, ModelManager
        classifier = LiveClassifier()
        if not classifier.is_available():
            err = ModelManager.get_instance().error or "AI model weights not found. Run: python scripts/initialize_weights.py"
            screening.status = "failed"
            db.commit()
            raise HTTPException(
                status_code=503,
                detail={"success": False, "error_code": "MODEL_NOT_READY", "message": err}
            )
        result = classifier.analyze_fundus(image, screening_id)

    except HTTPException:
        raise
    except Exception as e:
        screening.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error_code": "ANALYSIS_FAILED", "message": str(e)}
        )

    # ── Persist quality ───────────────────────────────────────────────────────
    db.query(ImageQualityResult).filter(ImageQualityResult.screening_id == screening_id).delete()
    db.add(ImageQualityResult(
        screening_id=screening_id,
        status=result["quality"]["status"],
        score=result["quality"]["score"],
        blur_score=result["quality"].get("blur_score"),
        brightness_score=result["quality"].get("brightness_score"),
        contrast_score=result["quality"].get("contrast_score"),
        retinal_visibility=result["quality"].get("retinal_visibility"),
        reasons=result["quality"].get("reasons"),
    ))

    # ── Persist prediction ────────────────────────────────────────────────────
    db.query(ModelPrediction).filter(ModelPrediction.screening_id == screening_id).delete()
    cls = result["classification"]
    db.add(ModelPrediction(
        screening_id=screening_id,
        model_name=cls["model_name"],
        model_version=cls["model_version"],
        predicted_grade=cls["predicted_grade"],
        predicted_label=cls["predicted_label"],
        probabilities=cls["probabilities"],
        confidence=cls["confidence"],
        calibration_status=cls["calibration_status"],
        mode=result["mode"],
    ))

    # ── Persist lesions ───────────────────────────────────────────────────────
    db.query(LesionFinding).filter(LesionFinding.screening_id == screening_id).delete()
    for les in result.get("lesions", []):
        db.add(LesionFinding(
            screening_id=screening_id,
            lesion_type=les["lesion_type"],
            status=les["status"],
            confidence=les.get("confidence"),
        ))

    # ── Persist explanation ───────────────────────────────────────────────────
    db.query(Explanation).filter(Explanation.screening_id == screening_id).delete()
    expl = result.get("explanation", {})
    db.add(Explanation(
        screening_id=screening_id,
        explanation_type=expl.get("explanation_type", "gradcam"),
        image_path=expl.get("image_url"),
        meta_data={"available": expl.get("available", False)},
    ))

    # ── Persist decision ──────────────────────────────────────────────────────
    db.query(DecisionRecord).filter(DecisionRecord.screening_id == screening_id).delete()
    dec = result["decision"]
    db.add(DecisionRecord(
        screening_id=screening_id,
        decision=dec["decision"],
        reason=dec["reason"],
        evidence_status=dec["evidence_status"],
    ))

    screening.status = "completed"
    screening.completed_at = datetime.utcnow()
    db.commit()

    return {"success": True, "data": result}


@router.get("/{screening_id}")
def get_screening(screening_id: int, db: Session = Depends(get_db)):
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found")

    patient = db.query(Patient).filter(Patient.id == screening.patient_id).first()
    img = db.query(UploadedImage).filter(UploadedImage.screening_id == screening_id).first()
    quality = db.query(ImageQualityResult).filter(ImageQualityResult.screening_id == screening_id).first()
    prediction = db.query(ModelPrediction).filter(ModelPrediction.screening_id == screening_id).first()
    lesions = db.query(LesionFinding).filter(LesionFinding.screening_id == screening_id).all()
    explanation = db.query(Explanation).filter(Explanation.screening_id == screening_id).first()
    decision = db.query(DecisionRecord).filter(DecisionRecord.screening_id == screening_id).first()
    review = db.query(ClinicianReview).filter(ClinicianReview.screening_id == screening_id).first()

    return {"success": True, "data": {
        "screening": {
            "id": screening.id, "patient_id": screening.patient_id, "status": screening.status,
            "mode": screening.mode, "eye_side": screening.eye_side,
            "created_at": screening.created_at.isoformat() if screening.created_at else None,
            "completed_at": screening.completed_at.isoformat() if screening.completed_at else None,
        },
        "patient": {
            "id": patient.id, "patient_code": patient.patient_code, "name": patient.name,
            "age": patient.age, "sex": patient.sex, "diabetes_status": patient.diabetes_status,
        } if patient else None,
        "image": {
            "id": img.id, "width": img.width, "height": img.height,
            "file_size": img.file_size, "url": f"/api/screenings/{screening_id}/image",
        } if img else None,
        "quality": {
            "status": quality.status, "score": quality.score,
            "blur_score": quality.blur_score, "brightness_score": quality.brightness_score,
            "contrast_score": quality.contrast_score, "retinal_visibility": quality.retinal_visibility,
            "reasons": quality.reasons,
        } if quality else None,
        "classification": {
            "model_name": prediction.model_name, "model_version": prediction.model_version,
            "predicted_grade": prediction.predicted_grade, "predicted_label": prediction.predicted_label,
            "probabilities": prediction.probabilities, "confidence": prediction.confidence,
            "calibration_status": prediction.calibration_status, "mode": prediction.mode,
        } if prediction else None,
        "lesions": [{"lesion_type": l.lesion_type, "status": l.status, "confidence": l.confidence} for l in lesions],
        "explanation": {
            "explanation_type": explanation.explanation_type,
            "image_url": f"/api/screenings/{screening_id}/gradcam" if explanation.image_path else None,
            "available": explanation.meta_data.get("available", False) if explanation.meta_data else False,
        } if explanation else None,
        "decision": {
            "decision": decision.decision, "reason": decision.reason, "evidence_status": decision.evidence_status,
        } if decision else None,
        "review": {
            "id": review.id, "clinical_assessment": review.clinical_assessment,
            "final_recommendation": review.final_recommendation, "notes": review.notes,
            "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None,
        } if review else None,
        "is_demo": False,
    }}


@router.post("/{screening_id}/review")
def save_review(screening_id: int, req: ReviewCreate, db: Session = Depends(get_db)):
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found")

    existing = db.query(ClinicianReview).filter(ClinicianReview.screening_id == screening_id).first()
    if existing:
        existing.clinical_assessment = req.clinical_assessment
        existing.final_recommendation = req.final_recommendation
        existing.notes = req.notes
        existing.reviewed_at = datetime.utcnow()
    else:
        db.add(ClinicianReview(
            screening_id=screening_id,
            clinical_assessment=req.clinical_assessment,
            final_recommendation=req.final_recommendation,
            notes=req.notes,
            reviewed_at=datetime.utcnow(),
        ))

    screening.status = "reviewed"
    db.commit()
    return {"success": True, "data": {"message": "Review saved"}}


@router.get("/{screening_id}/report")
def get_report(screening_id: int, db: Session = Depends(get_db)):
    return get_screening(screening_id, db)
