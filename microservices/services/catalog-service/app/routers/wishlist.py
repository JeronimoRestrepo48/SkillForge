from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course import Course
from app.models.wishlist import WishlistItem
from app.dependencies.auth import get_current_user, UserPayload
from app.schemas.catalog import WishlistItemOut, WishlistCreate, CourseOut

router = APIRouter()

@router.post("/wishlist", response_model=WishlistItemOut, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    item_in: WishlistCreate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == item_in.course_id, Course.status == "PUBLISHED").first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found."
        )
        
    existing = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.course_id == item_in.course_id
    ).first()
    
    if existing:
        return existing
        
    item = WishlistItem(
        user_id=current_user.id,
        course_id=item_in.course_id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/wishlist/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    item = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.course_id == course_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found."
        )
        
    db.delete(item)
    db.commit()
    return None

@router.get("/wishlist")
def get_my_wishlist(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    query = db.query(WishlistItem).filter(WishlistItem.user_id == current_user.id).order_by(WishlistItem.added_at.desc())
    total = query.count()
    start = (page - 1) * page_size
    results = query.offset(start).limit(page_size).all()
    
    end = start + page_size
    return {
        "count": total,
        "next": page + 1 if end < total else None,
        "previous": page - 1 if page > 1 else None,
        "results": [
            {
                "id": item.id,
                "user_id": item.user_id,
                "course_id": item.course_id,
                "added_at": item.added_at,
                "course": CourseOut.from_orm(item.course) if item.course else None
            } for item in results
        ]
    }
