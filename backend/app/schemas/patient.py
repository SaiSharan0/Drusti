from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    sex: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    diabetes_status: Optional[str] = None
    diabetes_duration: Optional[int] = None
    notes: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    patient_code: str
    name: str
    age: Optional[int]
    sex: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    diabetes_status: Optional[str]
    diabetes_duration: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PatientListItem(BaseModel):
    id: int
    patient_code: str
    name: str
    age: Optional[int]
    sex: Optional[str]
    location: Optional[str]
    diabetes_status: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
