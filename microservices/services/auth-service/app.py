import os
from datetime import datetime, timedelta, timezone

import jwt
from flask import Flask, jsonify, request
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

app = Flask(__name__)
Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///auth.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_MINUTES = int(os.getenv("JWT_ACCESS_MINUTES", "60"))
REFRESH_DAYS = int(os.getenv("JWT_REFRESH_DAYS", "7"))

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False)
    role = Column(String(32), nullable=False, default="student")


def _seed_users():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add_all(
                [
                    User(username="estudiante", password="estudiante123", email="estudiante@skillforge.local", role="student"),
                    User(username="instructor", password="instructor123", email="instructor@skillforge.local", role="instructor"),
                    User(username="admin", password="admin123", email="admin@skillforge.local", role="admin"),
                ]
            )
            db.commit()
    finally:
        db.close()


def _public_user(user: User):
    return {"id": user.id, "username": user.username, "email": user.email, "role": user.role}


def _make_token(user: User, token_type: str):
    now = datetime.now(tz=timezone.utc)
    expires_at = now + (timedelta(minutes=ACCESS_MINUTES) if token_type == "access" else timedelta(days=REFRESH_DAYS))
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _decode_token(raw_token: str):
    return jwt.decode(raw_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "auth-service"})


@app.post("/api/auth/verify")
def auth_verify():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"detail": "Missing bearer token"}), 401
    token = auth_header.replace("Bearer ", "", 1).strip()
    try:
        payload = _decode_token(token)
    except jwt.PyJWTError:
        return jsonify({"detail": "Invalid token"}), 401
    if payload.get("type") != "access":
        return jsonify({"detail": "Invalid token type"}), 401
    return jsonify(
        {
            "user_id": int(payload["sub"]),
            "username": payload["username"],
            "role": payload["role"],
            "token_type": payload["type"],
        }
    )


@app.get("/api/me")
def me():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"detail": "Authentication credentials were not provided."}), 401
    token = auth_header.replace("Bearer ", "", 1).strip()
    try:
        payload = _decode_token(token)
    except jwt.PyJWTError:
        return jsonify({"detail": "Invalid token"}), 401
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(payload["sub"])).first()
        if not user:
            return jsonify({"detail": "User not found"}), 404
        return jsonify(_public_user(user))
    finally:
        db.close()


@app.post("/api/token")
def token_obtain():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username, User.password == password).first()
        if not user:
            return jsonify({"detail": "No active account found with the given credentials"}), 401
        return jsonify({"access": _make_token(user, "access"), "refresh": _make_token(user, "refresh")})
    finally:
        db.close()


@app.post("/api/token/refresh")
def token_refresh():
    payload = request.get_json(silent=True) or {}
    refresh = str(payload.get("refresh", "")).strip()
    try:
        token_payload = _decode_token(refresh)
    except jwt.PyJWTError:
        return jsonify({"detail": "Token is invalid or expired"}), 401
    if token_payload.get("type") != "refresh":
        return jsonify({"detail": "Token is invalid or expired"}), 401
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(token_payload["sub"])).first()
        if not user:
            return jsonify({"detail": "User not found"}), 404
        return jsonify({"access": _make_token(user, "access")})
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
_seed_users()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
