import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserCreate, UserResponse, Token, UserLogin, TokenRefresh,
    TokenVerifyResponse, UserUpdateAdmin
)
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
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Solo permitir student o instructor en auto-registro
    allowed_roles = ["student", "instructor"]
    role = user_in.role if user_in.role in allowed_roles else "student"
    
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password=get_password_hash(user_in.password),
        role=role,
        nombre_completo=user_in.nombre_completo,
        telefono=user_in.telefono,
        ciudad=user_in.ciudad,
        pais=user_in.pais or "Colombia",
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

@router.get("/me/profile", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me/profile", response_model=UserResponse)
def update_my_profile(data: UserUpdateAdmin, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    safe_fields = {"nombre_completo", "telefono", "ciudad", "pais", "email"}
    for field, value in data.model_dump(exclude_unset=True).items():
        if field in safe_fields:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

@router.get("/users", response_model=list[UserResponse])
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return db.query(User).order_by(User.created_at.desc()).all()

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdateAdmin, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

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
