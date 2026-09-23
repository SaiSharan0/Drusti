from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.patient import Patient
from app.models.screening import Screening
from app.schemas.patient import PatientCreate, PatientResponse, PatientListItem
import uuid
from typing import Optional

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("")
def list_patients(
    search: Optional[str] = None,
    diabetes_status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Patient)
    if search:
        q = q.filter(
            (Patient.name.ilike(f"%{search}%")) | (Patient.patient_code.ilike(f"%{search}%"))
        )
    if diabetes_status:
        q = q.filter(Patient.diabetes_status == diabetes_status)
    total = q.count()
    patients = q.order_by(Patient.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    items = []
    for p in patients:
        last_screening = db.query(Screening).filter(Screening.patient_id == p.id).order_by(Screening.created_at.desc()).first()
        items.append({
            **PatientListItem.model_validate(p).model_dump(),
            "last_screening": last_screening.created_at.isoformat() if last_screening else None,
            "screening_count": db.query(Screening).filter(Screening.patient_id == p.id).count(),
        })

    return {"success": True, "data": {"patients": items, "total": total, "page": page, "limit": limit}}


@router.post("", response_model=dict)
def create_patient(req: PatientCreate, db: Session = Depends(get_db)):
    code = f"DRS-{uuid.uuid4().hex[:8].upper()}"
    patient = Patient(patient_code=code, **req.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return {"success": True, "data": PatientResponse.model_validate(patient).model_dump()}


@router.get("/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    screenings = db.query(Screening).filter(Screening.patient_id == patient_id).order_by(Screening.created_at.desc()).all()
    return {
        "success": True,
        "data": {
            "patient": PatientResponse.model_validate(patient).model_dump(),
            "screenings": [{"id": s.id, "status": s.status, "mode": s.mode, "eye_side": s.eye_side, "created_at": s.created_at.isoformat()} for s in screenings],
        },
    }
