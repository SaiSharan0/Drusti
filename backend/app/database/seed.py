"""Database seed — creates demo users and optional demo patients."""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.patient import Patient
from app.models.facility import Facility
from app.core.security import get_password_hash
import uuid


def seed_users(db: Session):
    if db.query(User).count() > 0:
        return
    users = [
        User(name="Dr. Priya Sharma", email="doctor@drusti.local", password_hash=get_password_hash("drusti123"), role="clinician"),
        User(name="Anita Devi", email="worker@drusti.local", password_hash=get_password_hash("drusti123"), role="health_worker"),
        User(name="Admin", email="admin@drusti.local", password_hash=get_password_hash("drusti123"), role="admin"),
    ]
    db.add_all(users)
    db.commit()


def seed_facilities(db: Session):
    from datetime import datetime
    if db.query(Facility).count() > 0:
        return
    facilities = [
        Facility(name="L V Prasad Eye Institute", facility_type="Specialist Hospital", address="Banjara Hills, Hyderabad", latitude=17.4237, longitude=78.4285, phone="040-68102020", website="https://www.lvpei.org/", notes="World-class eye care center", source_url="https://www.lvpei.org/", last_verified_at=datetime.utcnow()),
        Facility(name="Apollo Hospitals Hyderabad", facility_type="Multispecialty Hospital", address="Jubilee Hills, Hyderabad", latitude=17.4170, longitude=78.4069, phone="1860-500-1066", website="https://hyderabad.apollohospitals.com/", notes="Leading multispecialty hospital with eye care", source_url="https://hyderabad.apollohospitals.com/", last_verified_at=datetime.utcnow()),
        Facility(name="Yashoda Hospitals", facility_type="Multispecialty Hospital", address="Secunderabad, Hyderabad", latitude=17.4399, longitude=78.5005, phone="040-45674567", website="https://www.yashodahospitals.com/", notes="Comprehensive healthcare services", source_url="https://www.yashodahospitals.com/", last_verified_at=datetime.utcnow()),
        Facility(name="CARE Hospitals", facility_type="Multispecialty Hospital", address="Banjara Hills, Hyderabad", latitude=17.4140, longitude=78.4485, phone="040-61656565", website="https://www.carehospitals.com/", notes="Advanced eye and diabetes care", source_url="https://www.carehospitals.com/", last_verified_at=datetime.utcnow()),
        Facility(name="KIMS Hospitals", facility_type="Multispecialty Hospital", address="Secunderabad, Hyderabad", latitude=17.4410, longitude=78.4862, phone="040-44885000", website="https://www.kimshospitals.com/", notes="Provides specialized diabetic retinopathy screening", source_url="https://www.kimshospitals.com/", last_verified_at=datetime.utcnow()),
        Facility(name="Sankara Nethralaya Hyderabad", facility_type="Specialist Hospital", address="Secunderabad, Hyderabad", latitude=17.4520, longitude=78.4980, phone="040-27806565", website="https://www.sankaranethralaya.org/", notes="Dedicated eye care institute", source_url="https://www.sankaranethralaya.org/", last_verified_at=datetime.utcnow()),
    ]
    db.add_all(facilities)
    db.commit()


def run_seed(db: Session):
    seed_users(db)
    seed_facilities(db)

