from app.database.database import SessionLocal
from app.database.seed import run_seed

db = SessionLocal()
try:
    run_seed(db)
    print("Seed completed")
finally:
    db.close()
