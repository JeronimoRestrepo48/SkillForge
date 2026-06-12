from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    number = Column(String(40), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="PENDING")
    total = Column(Float, nullable=False, default=0.0)
    
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
