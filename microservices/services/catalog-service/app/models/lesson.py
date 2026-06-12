from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content_type = Column(String(20), nullable=False, default="TEXTO")  # VIDEO, TEXTO, QUIZ, PRACTICA
    content = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=1)
    duration_minutes = Column(Integer, nullable=False, default=0)

    module = relationship("Module", back_populates="lessons")
    progress_items = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")
