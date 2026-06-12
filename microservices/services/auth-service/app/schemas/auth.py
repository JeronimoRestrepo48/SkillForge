from pydantic import BaseModel

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

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenRefresh(BaseModel):
    refresh: str
