from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base
from datetime import datetime

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("course_prices.course_id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    status = Column(String(20), nullable=False, default="ACTIVA")
    created_at = Column(DateTime, default=datetime.utcnow)
