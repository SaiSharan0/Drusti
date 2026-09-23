import sqlalchemy
from app.core.config import get_settings

settings = get_settings()
engine = sqlalchemy.create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 0;"))
    conn.execute(sqlalchemy.text("DELETE FROM patients;"))
    conn.execute(sqlalchemy.text("DELETE FROM screenings;"))
    conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 1;"))
    conn.commit()
    print("Cleaned up demo patients and screenings.")
