from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course import Course
from app.dependencies.auth import get_current_user, UserPayload
from app.services.certification_progress import get_module_status

router = APIRouter()

@router.get("/courses/{course_id}/certification-progress")
def get_certification_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id, Course.status == "PUBLISHED").first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found."
        )
        
    if not course.es_certificacion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This course is not a certification course."
        )
        
    module_status = get_module_status(db, current_user.id, course)
    
    # Determinar si el certificado está disponible
    certificado_disponible = False
    modulo_final = next((m for m in module_status if m["es_examen_final"]), None)
    if modulo_final and modulo_final.get("aprobado") is True:
        certificado_disponible = True
        
    return {
        "course_id": course_id,
        "modules": module_status,
        "certificado_disponible": certificado_disponible
    }
