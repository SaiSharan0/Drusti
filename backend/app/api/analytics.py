from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.models.screening import Screening, DecisionRecord, ImageQualityResult, ModelPrediction

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("")
def get_analytics(db: Session = Depends(get_db)):
    total = db.query(Screening).count()
    clear = db.query(DecisionRecord).filter(DecisionRecord.decision == "clear").count()
    refer = db.query(DecisionRecord).filter(DecisionRecord.decision == "refer").count()
    escalate = db.query(DecisionRecord).filter(DecisionRecord.decision == "escalate").count()
    poor_quality = db.query(ImageQualityResult).filter(ImageQualityResult.status == "poor").count()
    demo = db.query(Screening).filter(Screening.mode == "demo").count()
    live = db.query(Screening).filter(Screening.mode == "live").count()

    # Grade distribution
    grade_dist = []
    for grade in range(5):
        count = db.query(ModelPrediction).filter(ModelPrediction.predicted_grade == grade).count()
        grade_dist.append({"grade": grade, "count": count})

    # Monthly screening trend (last 6 months)
    trend = (
        db.query(
            func.date_format(Screening.created_at, "%Y-%m").label("month"),
            func.count().label("count"),
        )
        .group_by("month")
        .order_by("month")
        .limit(12)
        .all()
    )
    monthly_trend = [{"month": t[0], "count": t[1]} for t in trend]

    return {
        "success": True,
        "data": {
            "total_screenings": total,
            "clear_count": clear,
            "refer_count": refer,
            "escalate_count": escalate,
            "poor_quality_count": poor_quality,
            "demo_count": demo,
            "live_count": live,
            "grade_distribution": grade_dist,
            "monthly_trend": monthly_trend,
        },
    }
