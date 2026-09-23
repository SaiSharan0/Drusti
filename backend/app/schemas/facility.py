from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FacilityCreate(BaseModel):
    name: str
    facility_type: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    source_url: Optional[str] = None
    last_verified_at: Optional[datetime] = None


class FacilityResponse(BaseModel):
    id: int
    name: str
    facility_type: str
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    phone: Optional[str]
    website: Optional[str]
    notes: Optional[str]
    source_url: Optional[str]
    last_verified_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class FacilityUpdate(BaseModel):
    name: Optional[str] = None
    facility_type: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    source_url: Optional[str] = None
    last_verified_at: Optional[datetime] = None
