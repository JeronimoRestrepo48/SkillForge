from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="PUBLISHED")
    nivel_dificultad = Column(String(20), nullable=False, default="PRINCIPIANTE")
    duracion_horas = Column(Integer, default=0)
    instructor_id = Column(Integer, nullable=False)

    category = relationship("Category", back_populates="courses")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="course", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="course", cascade="all, delete-orphan")
