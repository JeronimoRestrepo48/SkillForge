from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("course_prices.course_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
