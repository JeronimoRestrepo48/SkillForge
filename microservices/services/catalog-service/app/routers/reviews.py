from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course import Course
from app.models.rating import Rating
from app.dependencies.auth import get_current_user, UserPayload
from app.schemas.catalog import RatingOut, RatingCreate

router = APIRouter()

@router.post("/courses/{course_id}/review", response_model=RatingOut, status_code=status.HTTP_201_CREATED)
@router.post("/courses/{course_id}/rate", response_model=RatingOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_course_review(
    course_id: int,
    review_in: RatingCreate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id, Course.status == "PUBLISHED").first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found."
        )
        
    existing = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.course_id == course_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already rated this course."
        )
        
    rating = Rating(
        course_id=course_id,
        user_id=current_user.id,
        score=review_in.score,
        comment=review_in.comment
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating

@router.get("/courses/{course_id}/reviews")
@router.get("/courses/{course_id}/ratings", include_in_schema=False)
def list_course_reviews(
    course_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id, Course.status == "PUBLISHED").first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found."
        )
        
    query = db.query(Rating).filter(Rating.course_id == course_id).order_by(Rating.created_at.desc())
    total = query.count()
    start = (page - 1) * page_size
    results = query.offset(start).limit(page_size).all()
    
    end = start + page_size
    return {
        "count": total,
        "next": page + 1 if end < total else None,
        "previous": page - 1 if page > 1 else None,
        "results": [RatingOut.from_orm(r) for r in results]
    }
