from pydantic import BaseModel
from typing import Optional

class InstructorProfileBase(BaseModel):
    bio: Optional[str] = None
    carrera: Optional[str] = None
    estudios: Optional[str] = None
    linkedin_url: Optional[str] = None
    sitio_web: Optional[str] = None
    avatar_url: Optional[str] = None

class InstructorProfileUpdate(InstructorProfileBase):
    pass

class InstructorProfileOut(InstructorProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
