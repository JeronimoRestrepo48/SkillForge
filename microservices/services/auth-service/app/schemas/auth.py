from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Token(BaseModel):
    access: str
    refresh: str

class TokenData(BaseModel):
    sub: str
    username: str
    role: str
    type: str

class TokenVerifyResponse(BaseModel):
    user_id: int
    username: str
    role: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "student"
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = "Colombia"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class TokenRefresh(BaseModel):
    refresh: str

class UserUpdateAdmin(BaseModel):
    role: Optional[str] = None
    nombre_completo: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
