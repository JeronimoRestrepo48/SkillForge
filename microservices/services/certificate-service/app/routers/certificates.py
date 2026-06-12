from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
import requests
import logging
import datetime
import random
import string
from jose import jwt

from app.database import get_db
from app.config import settings
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateCheckRequest, CertificateOut, CertificateVerifyOut
from app.dependencies.auth import get_current_user, UserPayload

logger = logging.getLogger("certificates")

router = APIRouter()


def check_and_issue_logic(req: CertificateCheckRequest, db: Session):
    existing = db.query(Certificate).filter(
        Certificate.user_id == req.user_id,
        Certificate.course_id == req.course_id
    ).first()
    if existing:
        logger.info(f"Certificate already exists for user_id={req.user_id}, course_id={req.course_id}")
        return existing

    token_payload = {
        "sub": str(req.user_id),
        "username": "system_certificate",
        "role": "admin",
        "type": "access"
    }
    token = jwt.encode(token_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        progress_url = f"{settings.CATALOG_SERVICE_URL}/api/catalog/courses/{req.course_id}/progress"
        progress_resp = requests.get(progress_url, headers=headers, timeout=10)
        if progress_resp.status_code != 200:
            logger.error(f"Catalog service returned status {progress_resp.status_code} for progress check")
            raise HTTPException(status_code=400, detail="Could not verify student progress.")
            
        progress_data = progress_resp.json()
        if not progress_data.get("completed", False) or progress_data.get("percentage", 0.0) < 100.0:
            raise HTTPException(
                status_code=400,
                detail=f"Student has not completed the course. Current progress: {progress_data.get('percentage', 0.0)}%"
            )
            
        course_url = f"{settings.CATALOG_SERVICE_URL}/api/catalog/courses/{req.course_id}"
        course_resp = requests.get(course_url, headers=headers, timeout=10)
        if course_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Course details not found.")
        course_data = course_resp.json()
        course_title = course_data.get("title", f"Course #{req.course_id}")
        
        auth_url = "http://auth-service:8000/auth/me"
        auth_resp = requests.get(auth_url, headers=headers, timeout=10)
        if auth_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Student user details not found.")
        auth_data = auth_resp.json()
        student_name = auth_data.get("username", "Student").capitalize()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Upstream communication failure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to communicate with catalog or auth microservice."
        )
        
    year = datetime.datetime.now().strftime("%Y")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    numero_certificado = f"SF-CERT-{year}-{suffix}"
    
    codigo_verificacion = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    while db.query(Certificate).filter(Certificate.codigo_verificacion == codigo_verificacion).first():
        codigo_verificacion = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
    fecha_emision = datetime.datetime.now()
    
    cert = Certificate(
        user_id=req.user_id,
        course_id=req.course_id,
        course_title=course_title,
        student_name=student_name,
        numero_certificado=numero_certificado,
        codigo_verificacion=codigo_verificacion,
        fecha_emision=fecha_emision,
        status="PENDING",
        plantilla="default"
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    
    # Despachar tarea asíncrona de Celery
    from app.celery_client import celery_app
    task_data = {
        "certificado_id": cert.id,
        "nombre_usuario": student_name,
        "curso_titulo": course_title,
        "numero_certificado": numero_certificado,
        "codigo_verificacion": codigo_verificacion,
        "fecha_emision": fecha_emision.isoformat()
    }
    
    task = celery_app.send_task(
        "shared.tasks.documents.generar_pdf_certificado_async",
        kwargs={"data": task_data},
        queue="documents"
    )
    
    cert.task_id = task.id
    db.commit()
    db.refresh(cert)
    
    logger.info(f"Certificate {numero_certificado} task dispatched. Task ID: {task.id}")
    return cert

@router.post("/check-and-issue", response_model=CertificateOut, status_code=status.HTTP_201_CREATED)
def check_and_issue(
    req: CertificateCheckRequest,
    db: Session = Depends(get_db)
):
    return check_and_issue_logic(req, db)

@router.post("/internal/check-pending-tasks")
def check_pending_tasks(db: Session = Depends(get_db)):
    from app.celery_client import celery_app
    pending_certs = db.query(Certificate).filter(Certificate.status == "PENDING", Certificate.task_id.isnot(None)).all()
    updated = 0
    for cert in pending_certs:
        res = celery_app.AsyncResult(cert.task_id)
        if res.ready():
            if res.successful():
                result_data = res.result
                cert.status = "COMPLETED"
                cert.pdf_url = result_data.get('s3_url')
                logger.info(f"Certificate {cert.id} COMPLETED. URL: {cert.pdf_url}")
            else:
                cert.status = "FAILED"
                logger.error(f"Certificate {cert.id} task FAILED.")
            db.commit()
            updated += 1
    return {"status": "ok", "checked": len(pending_certs), "updated": updated}

@router.get("/verify/{code}", response_model=CertificateVerifyOut)
def verify_certificate(
    code: str,
    db: Session = Depends(get_db)
):
    """
    Ruta pública para verificar un certificado a través de su código único de verificación.
    """
    cert = db.query(Certificate).filter(Certificate.codigo_verificacion == code.strip().upper()).first()
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found with the provided verification code."
        )
        
    # Formatear la fecha a español
    meses = (
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    )
    dt = cert.fecha_emision
    fecha_formateada = f"{dt.day} de {meses[dt.month - 1]} de {dt.year}"
    
    return CertificateVerifyOut(
        valid=True,
        student_name=cert.student_name,
        course_title=cert.course_title,
        completion_date=fecha_formateada,
        issuer="SkillForge Active Learning Academy",
        verification_code=cert.codigo_verificacion,
        status="VERIFICADO",
        pdf_url=cert.pdf_url
    )

@router.get("/my-certificates", response_model=List[CertificateOut])
def get_my_certificates(
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    """
    Retorna la lista de todos los certificados del estudiante logueado.
    """
    certs = db.query(Certificate).filter(Certificate.user_id == current_user.id).order_by(Certificate.fecha_emision.desc()).all()
    return certs

@router.get("/{certificate_id}/pdf")
def download_certificate_pdf(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    """
    Descarga al vuelo el archivo PDF de un certificado por ID.
    Si S3 está activo, redirige directamente a la URL de S3.
    """
    cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found.")
        
    # Si tiene una URL externa de S3, redirigir
    if cert.pdf_url and cert.pdf_url.startswith("http"):
        return RedirectResponse(url=cert.pdf_url)
        
    raise HTTPException(status_code=400, detail="Certificate PDF is still being generated or is unavailable.")
