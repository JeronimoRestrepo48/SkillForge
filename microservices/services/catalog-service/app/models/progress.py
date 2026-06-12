from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    lesson = relationship("Lesson", back_populates="progress_items")

    __table_args__ = (UniqueConstraint('user_id', 'lesson_id', name='_user_lesson_uc'),)
