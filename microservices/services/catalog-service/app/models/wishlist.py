from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="wishlist_items")

    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='_user_course_wishlist_uc'),)
