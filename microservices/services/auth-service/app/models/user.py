from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False)
    role = Column(String(32), nullable=False, default="student")
    nombre_completo = Column(String(200), nullable=True)
    telefono = Column(String(20), nullable=True)
    ciudad = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=True, default="Colombia")
    created_at = Column(DateTime, default=datetime.utcnow)
