from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models.lesson import Lesson
from app.models.progress import LessonProgress
from app.models.course import Course
from app.models.module import Module
from app.dependencies.auth import get_current_user, UserPayload
from app.schemas.catalog import LessonProgressOut

router = APIRouter()

@router.post("/lessons/{lesson_id}/complete", response_model=LessonProgressOut, status_code=status.HTTP_200_OK)
def complete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found."
        )
        
    course = db.query(Course).join(Module).filter(Module.id == lesson.module_id).first()
    if course and course.es_certificacion:
        from app.services.certification_progress import get_module_status
        module_status = get_module_status(db, current_user.id, course)
        modulo_actual = next((m for m in module_status if m["module_id"] == lesson.module_id), None)
        if modulo_actual and modulo_actual.get("bloqueado"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Debes aprobar el examen del módulo anterior para acceder a esta lección."
            )
            
    progress = db.query(LessonProgress).filter(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id == lesson_id
    ).first()
    
    if progress:
        progress.completed = True
        progress.completed_at = datetime.now(timezone.utc)
    else:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(progress)
        
    db.commit()
    db.refresh(progress)
    return progress
