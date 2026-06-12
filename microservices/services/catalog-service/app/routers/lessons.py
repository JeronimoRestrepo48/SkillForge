from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models.lesson import Lesson
from app.models.progress import LessonProgress
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
