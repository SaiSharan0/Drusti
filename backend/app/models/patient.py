from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String(30), nullable=True)
    phone = Column(String(30), nullable=True)
    location = Column(String(255), nullable=True)
    diabetes_status = Column(String(30), nullable=True)  # known, unknown, none
    diabetes_duration = Column(Integer, nullable=True)  # years
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
