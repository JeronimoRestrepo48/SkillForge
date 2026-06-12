from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.enrollment import Enrollment
from app.dependencies.auth import get_current_user, UserPayload
from app.schemas.transactions import EnrollmentOut

router = APIRouter()

@router.get("/enrollments")
def list_enrollments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    query = db.query(Enrollment).filter(Enrollment.user_id == current_user.id).order_by(Enrollment.id.desc())
    total = query.count()
    start = (page - 1) * page_size
    results = query.offset(start).limit(page_size).all()
    
    end = start + page_size
    return {
        "count": total,
        "next": page + 1 if end < total else None,
        "previous": page - 1 if page > 1 else None,
        "results": [EnrollmentOut.from_orm(r) for r in results]
    }

@router.get("/enrollments/{enrollment_id}", response_model=EnrollmentOut)
def get_enrollment_detail(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id,
        Enrollment.user_id == current_user.id
    ).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found."
        )
    return enrollment
