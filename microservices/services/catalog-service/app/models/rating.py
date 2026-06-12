from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    score = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="ratings")

    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='_user_course_rating_uc'),)
