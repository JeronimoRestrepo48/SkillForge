from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Trayectoria(Base):
    __tablename__ = "trayectorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria_general = Column(String(100), nullable=True)
    imagen_url = Column(String(500), nullable=True)
    cursos = relationship("TrayectoriaCurso", back_populates="trayectoria", cascade="all, delete-orphan", order_by="TrayectoriaCurso.sort_order")

class TrayectoriaCurso(Base):
    __tablename__ = "trayectoria_cursos"
    id = Column(Integer, primary_key=True, index=True)
    trayectoria_id = Column(Integer, ForeignKey("trayectorias.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    sort_order = Column(Integer, nullable=False, default=1)
    trayectoria = relationship("Trayectoria", back_populates="cursos")
    course = relationship("Course")
