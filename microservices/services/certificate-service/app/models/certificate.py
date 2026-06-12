from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    course_title = Column(String(200), nullable=False)
    student_name = Column(String(150), nullable=False)
    numero_certificado = Column(String(50), unique=True, nullable=False, index=True)
    codigo_verificacion = Column(String(20), unique=True, nullable=False, index=True)
    fecha_emision = Column(DateTime, server_default=func.now(), nullable=False)
    pdf_url = Column(String(500), nullable=True)
    plantilla = Column(String(50), nullable=False, default="default")
    status = Column(String(20), nullable=False, default="PENDING")
    task_id = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='_user_course_uc'),
    )
