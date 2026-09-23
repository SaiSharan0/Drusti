from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.facility import Facility
from app.schemas.facility import FacilityCreate, FacilityResponse, FacilityUpdate
from typing import Optional

router = APIRouter(prefix="/api/facilities", tags=["facilities"])


@router.get("")
def list_facilities(
    facility_type: Optional[str] = None,
    search: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Facility)
    if facility_type:
        q = q.filter(Facility.facility_type == facility_type)
    if search:
        q = q.filter(Facility.name.ilike(f"%{search}%") | Facility.address.ilike(f"%{search}%"))
    facilities = q.order_by(Facility.name).all()
    return {
        "success": True,
        "data": [FacilityResponse.model_validate(f).model_dump() for f in facilities],
        "count": len(facilities),
    }


@router.post("")
def create_facility(req: FacilityCreate, db: Session = Depends(get_db)):
    f = Facility(**req.model_dump())
    db.add(f)
    db.commit()
    db.refresh(f)
    return {"success": True, "data": FacilityResponse.model_validate(f).model_dump()}


@router.put("/{facility_id}")
def update_facility(facility_id: int, req: FacilityUpdate, db: Session = Depends(get_db)):
    f = db.query(Facility).filter(Facility.id == facility_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facility not found")
    for key, val in req.model_dump(exclude_unset=True).items():
        setattr(f, key, val)
    db.commit()
    return {"success": True, "data": FacilityResponse.model_validate(f).model_dump()}


@router.delete("/{facility_id}")
def delete_facility(facility_id: int, db: Session = Depends(get_db)):
    f = db.query(Facility).filter(Facility.id == facility_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facility not found")
    db.delete(f)
    db.commit()
    return {"success": True, "data": {"message": "Facility deleted"}}
