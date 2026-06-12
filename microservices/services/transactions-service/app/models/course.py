from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class CoursePrice(Base):
    __tablename__ = "course_prices"
    course_id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    price = Column(Float, nullable=False)
