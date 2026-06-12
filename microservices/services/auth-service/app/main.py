from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.routers import auth
from app.models.user import User
from app.services.auth_service import get_password_hash

# Generate tables
Base.metadata.create_all(bind=engine)

def seed_users():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            users = [
                User(username="estudiante", password=get_password_hash("estudiante123"), email="estudiante@skillforge.local", role="student"),
                User(username="instructor", password=get_password_hash("instructor123"), email="instructor@skillforge.local", role="instructor"),
                User(username="admin", password=get_password_hash("admin123"), email="admin@skillforge.local", role="admin"),
            ]
            # Sanity check: ensure passwords are actually hashed
            for u in users:
                assert u.password.startswith("$2"), \
                    f"Password for {u.username} is not a valid bcrypt hash! Got: {u.password[:10]}"
            db.add_all(users)
            db.commit()
    finally:
        db.close()

seed_users()

app = FastAPI(title="SkillForge Auth Service")

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# Add backwards compatibility endpoints for gateway/existing structure
app.include_router(auth.router, prefix="/api", tags=["legacy"])
