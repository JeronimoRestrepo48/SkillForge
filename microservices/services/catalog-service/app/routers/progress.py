from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course import Course
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.progress import LessonProgress
from app.dependencies.auth import get_current_user, UserPayload
from app.schemas.catalog import CourseProgressOut

router = APIRouter()

@router.get("/courses/{course_id}/progress", response_model=CourseProgressOut)
def get_course_progress(
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
        
    # Get all lessons in this course
    lessons = db.query(Lesson).join(Module).filter(Module.course_id == course_id).all()
    lesson_ids = [l.id for l in lessons]
    
    total_lessons = len(lesson_ids)
    if total_lessons == 0:
        return CourseProgressOut(
            course_id=course_id,
            total_lessons=0,
            completed_lessons=0,
            percentage=0.0,
            completed=False,
            completed_lesson_ids=[]
        )
        
    completed_progress = db.query(LessonProgress.lesson_id).filter(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id.in_(lesson_ids),
        LessonProgress.completed == True
    ).all()
    completed_ids = [p[0] for p in completed_progress]
    
    completed_progress_count = len(completed_ids)
    percentage = round((completed_progress_count / total_lessons) * 100, 2)
    completed = completed_progress_count == total_lessons
    
    return CourseProgressOut(
        course_id=course_id,
        total_lessons=total_lessons,
        completed_lessons=completed_progress_count,
        percentage=percentage,
        completed=completed,
        completed_lesson_ids=completed_ids
    )
