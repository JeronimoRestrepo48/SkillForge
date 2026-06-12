from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.module import Module
from app.models.lesson import Lesson
from app.schemas.catalog import LessonOut

router = APIRouter()

@router.get("/modules/{module_id}/lessons")
def get_module_lessons(
    module_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found."
        )
        
    query = db.query(Lesson).filter(Lesson.module_id == module.id).order_by(Lesson.sort_order.asc())
    total = query.count()
    start = (page - 1) * page_size
    results = query.offset(start).limit(page_size).all()
    
    end = start + page_size
    return {
        "count": total,
        "next": page + 1 if end < total else None,
        "previous": page - 1 if page > 1 else None,
        "results": [LessonOut.from_orm(l) for l in results]
    }
