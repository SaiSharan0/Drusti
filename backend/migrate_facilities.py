import sqlalchemy
from app.core.config import get_settings

settings = get_settings()
engine = sqlalchemy.create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    try:
        conn.execute(sqlalchemy.text("ALTER TABLE facilities ADD COLUMN source_url VARCHAR(500);"))
        print("Added source_url")
    except Exception as e:
        print(e)
        
    try:
        conn.execute(sqlalchemy.text("ALTER TABLE facilities ADD COLUMN last_verified_at DATETIME;"))
        print("Added last_verified_at")
    except Exception as e:
        print(e)
    
    conn.commit()
