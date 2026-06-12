from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.order import Order
from app.dependencies.auth import get_current_user, UserPayload
from app.schemas.transactions import OrderOut

router = APIRouter()

@router.get("/orders")
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    query = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.id.desc())
    total = query.count()
    start = (page - 1) * page_size
    results = query.offset(start).limit(page_size).all()
    
    end = start + page_size
    return {
        "count": total,
        "next": page + 1 if end < total else None,
        "previous": page - 1 if page > 1 else None,
        "results": [OrderOut.from_orm(r) for r in results]
    }

@router.get("/orders/{order_identifier}", response_model=OrderOut)
def get_order_detail(
    order_identifier: str,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    # Try searching by number first, then by database id if numeric
    order = db.query(Order).filter(Order.number == order_identifier, Order.user_id == current_user.id).first()
    if not order and order_identifier.isdigit():
        order = db.query(Order).filter(Order.id == int(order_identifier), Order.user_id == current_user.id).first()
        
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
    return order
