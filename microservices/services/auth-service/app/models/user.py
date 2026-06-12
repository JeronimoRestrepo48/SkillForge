from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False)
    role = Column(String(32), nullable=False, default="student")
