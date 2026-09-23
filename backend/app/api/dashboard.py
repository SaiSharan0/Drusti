from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime
from app.database.database import get_db
from app.models.screening import Screening, DecisionRecord, ImageQualityResult, ModelPrediction, ClinicianReview
from app.models.patient import Patient

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    today = date.today()
    total = db.query(Screening).count()
    today_count = db.query(Screening).filter(func.date(Screening.created_at) == today).count()

    clear = db.query(DecisionRecord).filter(DecisionRecord.decision == "clear").count()
    refer = db.query(DecisionRecord).filter(DecisionRecord.decision == "refer").count()
    escalate = db.query(DecisionRecord).filter(DecisionRecord.decision == "escalate").count()
    poor_quality = db.query(ImageQualityResult).filter(ImageQualityResult.status == "poor").count()
    pending = db.query(Screening).filter(Screening.status.in_(["completed", "needs_review"])).count()
    reviewed = db.query(ClinicianReview).count()

    recent = (
        db.query(Screening, Patient.name, Patient.patient_code)
        .join(Patient, Patient.id == Screening.patient_id)
        .order_by(Screening.created_at.desc())
        .limit(10)
        .all()
    )

    recent_list = []
    for s, pname, pcode in recent:
        qual = db.query(ImageQualityResult).filter(ImageQualityResult.screening_id == s.id).first()
        pred = db.query(ModelPrediction).filter(ModelPrediction.screening_id == s.id).first()
        dec = db.query(DecisionRecord).filter(DecisionRecord.screening_id == s.id).first()
        rev = db.query(ClinicianReview).filter(ClinicianReview.screening_id == s.id).first()
        recent_list.append({
            "id": s.id,
            "patient_name": pname,
            "patient_code": pcode,
            "date": s.created_at.isoformat() if s.created_at else None,
            "status": s.status,
            "mode": s.mode,
            "quality": qual.status if qual else None,
            "prediction": pred.predicted_label if pred else None,
            "decision": dec.decision if dec else None,
            "reviewed": rev is not None,
        })

    return {
        "success": True,
        "data": {
            "total_screenings": total,
            "today_screenings": today_count,
            "clear_count": clear,
            "refer_count": refer,
            "escalate_count": escalate,
            "poor_quality_count": poor_quality,
            "pending_review": pending - reviewed,
            "recent_screenings": recent_list,
        },
    }
