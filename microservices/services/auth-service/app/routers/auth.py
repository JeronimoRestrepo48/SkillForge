import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse, Token, UserLogin, TokenRefresh, TokenVerifyResponse
from app.services.auth_service import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, decode_token, is_pbkdf2_hash
)
from app.dependencies.auth import get_current_user
from jose import JWTError

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password=hashed_password,
        role="student"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/token", response_model=Token)
def login_for_access_token(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user or not verify_password(user_in.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # Migración transparente: si el hash aún es pbkdf2 (importado de Django),
    # re-hasheamos con bcrypt en este primer login exitoso.
    # El usuario no nota nada — a partir de aquí usa bcrypt.
    if is_pbkdf2_hash(user.password):
        user.password = get_password_hash(user_in.password)
        db.commit()
        logger.info(
            "Password migrated pbkdf2→bcrypt for user '%s' (id=%s)",
            user.username, user.id
        )

    return {
        "access": create_access_token(user),
        "refresh": create_refresh_token(user)
    }

@router.post("/token/refresh", response_model=dict)
def refresh_token(token_in: TokenRefresh, db: Session = Depends(get_db)):
    try:
        payload = decode_token(token_in.refresh)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"access": create_access_token(user)}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/verify", response_model=TokenVerifyResponse)
def verify_token(request: Request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth_header.replace("Bearer ", "", 1).strip()
    
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return {
            "user_id": int(payload["sub"]),
            "username": payload["username"],
            "role": payload["role"],
            "token_type": payload["type"]
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
