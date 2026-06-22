from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base

class InstructorProfile(Base):
    __tablename__ = "instructor_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    bio = Column(Text, nullable=True)
    carrera = Column(String(200), nullable=True)
    estudios = Column(Text, nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    sitio_web = Column(String(255), nullable=True)
    avatar_url = Column(String(255), nullable=True)
