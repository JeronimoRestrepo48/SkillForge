from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CertificateCheckRequest(BaseModel):
    user_id: int
    course_id: int

class CertificateOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    course_title: str
    student_name: str
    numero_certificado: str
    codigo_verificacion: str
    fecha_emision: datetime
    pdf_url: Optional[str]
    plantilla: str

    class Config:
        from_attributes = True

class CertificateVerifyOut(BaseModel):
    valid: bool
    student_name: str
    course_title: str
    completion_date: str
    issuer: str
    verification_code: str
    status: str
    pdf_url: Optional[str]
