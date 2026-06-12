from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CartItemAdd(BaseModel):
    course_id: int
    quantity: int = Field(1, ge=1)

class CartItemRemove(BaseModel):
    course_id: int

class CartItemOut(BaseModel):
    course_id: int
    course_title: str
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True

class CartOut(BaseModel):
    count: int
    results: List[CartItemOut]
    total: float

class OrderOut(BaseModel):
    id: int
    number: str
    user_id: int
    status: str
    total: float

    class Config:
        from_attributes = True

class EnrollmentOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    order_id: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class CouponValidate(BaseModel):
    coupon_code: str

class CouponValidationResult(BaseModel):
    valid: bool
    code: str
    discount_percentage: float
    description: str

class QuoteItem(BaseModel):
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., ge=0.0)

class QuoteRequest(BaseModel):
    items: List[QuoteItem]
    coupon_code: Optional[str] = None

class QuoteResponse(BaseModel):
    engine: str
    items_count: int
    subtotal: float
    discounts: float
    total: float
    currency: str
