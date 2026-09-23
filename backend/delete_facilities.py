import sqlalchemy
from app.core.config import get_settings

settings = get_settings()
engine = sqlalchemy.create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    conn.execute(sqlalchemy.text("DELETE FROM facilities;"))
    conn.commit()
    print("Deleted old facilities")
