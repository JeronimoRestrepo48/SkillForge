from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cart import CartItem
from app.models.course import CoursePrice
from app.dependencies.auth import get_current_user, UserPayload
from app.schemas.transactions import CartOut, CartItemOut, CartItemAdd, CartItemRemove

router = APIRouter()

@router.get("/cart", response_model=CartOut)
def get_cart(
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).order_by(CartItem.id.asc()).all()
    detailed = []
    total = 0.0
    for item in items:
        course = db.query(CoursePrice).filter(CoursePrice.course_id == item.course_id).first()
        if not course:
            continue
        subtotal = course.price * item.quantity
        total += subtotal
        detailed.append(
            CartItemOut(
                course_id=item.course_id,
                course_title=course.title,
                quantity=item.quantity,
                unit_price=course.price,
                subtotal=round(subtotal, 2)
            )
        )
    return CartOut(
        count=len(detailed),
        results=detailed,
        total=round(total, 2)
    )

@router.post("/cart/items", status_code=status.HTTP_201_CREATED)
@router.post("/cart/add", status_code=status.HTTP_201_CREATED, include_in_schema=False)
def add_to_cart(
    item_in: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    course = db.query(CoursePrice).filter(CoursePrice.course_id == item_in.course_id).first()
    if not course:
        import requests
        try:
            resp = requests.get(f"http://catalog-service:8000/api/catalog/courses/{item_in.course_id}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                course = CoursePrice(course_id=data["id"], title=data["title"], price=data["price"])
                db.add(course)
                db.commit()
                db.refresh(course)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found."
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found or unavailable."
            )
    existing = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.course_id == item_in.course_id
    ).first()
    if existing:
        existing.quantity += item_in.quantity
    else:
        db.add(CartItem(user_id=current_user.id, course_id=item_in.course_id, quantity=item_in.quantity))
    db.commit()
    return {"detail": "Course added to cart."}

@router.post("/cart/remove", status_code=status.HTTP_200_OK, include_in_schema=False)
def remove_from_cart_legacy(
    item_in: CartItemRemove,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.course_id == item_in.course_id
    ).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not in cart."
        )
    db.delete(item)
    db.commit()
    return {"detail": "Course removed from cart."}

@router.delete("/cart/items/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.course_id == course_id
    ).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not in cart."
        )
    db.delete(item)
    db.commit()
    return None
