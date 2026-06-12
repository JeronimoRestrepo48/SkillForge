from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from app.database import get_db
from app.models.cart import CartItem
from app.models.course import CoursePrice
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.enrollment import Enrollment
from app.dependencies.auth import get_current_user, UserPayload
from app.schemas.transactions import (
    QuoteRequest, QuoteResponse, CouponValidate, CouponValidationResult, OrderOut
)
from app.services.wompi_gateway import WompiPaymentGateway
from app.config import settings
from app.celery_client import celery_app

logger = logging.getLogger("transactions")

router = APIRouter()

COUPON_RULES = {
    "WELCOME10": 0.10,
    "STUDENT15": 0.15,
}

class CheckoutReturnRequest(BaseModel):
    order_number: str
    result: str

class WompiParamsResponse(BaseModel):
    public_key: str
    signature: str
    amount_in_cents: int
    reference: str
    currency: str
    redirect_url: str

def _apply_coupon(subtotal: float, coupon_code: Optional[str]) -> float:
    if not coupon_code:
        return 0.0
    code = coupon_code.strip().upper()
    percentage = COUPON_RULES.get(code)
    if percentage is None:
        raise ValueError("Coupon code is invalid.")
    return round(subtotal * percentage, 2)

@router.post("/coupons/validate", response_model=CouponValidationResult)
def validate_coupon(data: CouponValidate):
    code = data.coupon_code.strip().upper()
    percentage = COUPON_RULES.get(code)
    if percentage is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon code is invalid."
        )
    return CouponValidationResult(
        valid=True,
        code=code,
        discount_percentage=percentage * 100.0,
        description=f"{int(percentage * 100)}% discount applied."
    )

@router.post("/checkout/quote", response_model=QuoteResponse)
def get_checkout_quote(req: QuoteRequest):
    if not req.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'items' must be a non-empty array."
        )
    try:
        subtotal = round(sum(i.quantity * i.unit_price for i in req.items), 2)
        discounts = _apply_coupon(subtotal, req.coupon_code)
        total = round(max(subtotal - discounts, 0.0), 2)
        
        return QuoteResponse(
            engine="transactions-service",
            items_count=len(req.items),
            subtotal=subtotal,
            discounts=discounts,
            total=total,
            currency="COP"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/checkout/confirm", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def checkout_confirm(
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    cart = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your cart is empty."
        )
        
    total = 0.0
    items_to_create = []
    
    for item in cart:
        course = db.query(CoursePrice).filter(CoursePrice.course_id == item.course_id).first()
        if course:
            price_subtotal = course.price * item.quantity
            total += price_subtotal
            items_to_create.append({
                "course_id": item.course_id,
                "price": course.price,
                "quantity": item.quantity
            })
            
    last_order = db.query(Order.id).order_by(Order.id.desc()).first()
    next_id = (last_order[0] if last_order else 0) + 1
    number = f"SF-{10000 + next_id}"
    
    order = Order(
        number=number,
        user_id=current_user.id,
        status="PENDING",
        total=round(total, 2)
    )
    db.add(order)
    db.flush()
    
    # Crear OrderItems históricos
    for item_data in items_to_create:
        order_item = OrderItem(
            order_id=order.id,
            course_id=item_data["course_id"],
            price=item_data["price"],
            quantity=item_data["quantity"]
        )
        db.add(order_item)
        
    db.commit()
    db.refresh(order)
    return order

@router.post("/checkout/return", response_model=OrderOut)
def checkout_return(
    payload: CheckoutReturnRequest,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.number == payload.order_number,
        Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
        
    res = payload.result.lower()
    if res == "success":
        if order.status == "PENDING":
            # Crear inscripciones basadas en los OrderItems persistentes
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            for item in order_items:
                existing = db.query(Enrollment).filter(
                    Enrollment.user_id == current_user.id,
                    Enrollment.course_id == item.course_id
                ).first()
                if not existing:
                    enrollment = Enrollment(
                        user_id=current_user.id,
                        course_id=item.course_id,
                        order_id=order.id,
                        status="ACTIVA"
                    )
                    db.add(enrollment)
            
            order.status = "CONFIRMED"
            # Limpiar el carrito del usuario
            db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
            db.commit()
            
            # Despachar tarea de email de confirmación (cola high_priority)
            try:
                # Obtenemos email y nombre (simulado o a través del token)
                # Como tenemos el user_id, y asumimos que el token tiene email:
                user_email = current_user.email if hasattr(current_user, 'email') else f"user{current_user.id}@skillforge.local"
                user_name = "Estudiante" # Opcional: obtener del microservicio de auth si estuviera disponible
                
                celery_app.send_task(
                    "shared.tasks.notifications.enviar_notificacion_orden_async",
                    kwargs={
                        "data": {
                            "email": user_email,
                            "nombre_usuario": user_name,
                            "numero_orden": order.number
                        }
                    },
                    queue="high_priority"
                )
                
                # Publicar evento de orden completada
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../../"))
                from shared.event_bus import RedisEventBus
                
                bus = RedisEventBus()
                for item in order_items:
                    bus.publish(
                        stream="ordenes",
                        event_type="orden.completada",
                        data={
                            "user_id": current_user.id,
                            "course_id": item.course_id,
                            "order_number": order.number
                        }
                    )
            except Exception as e:
                logger.error(f"Error dispatching Celery tasks on local return: {str(e)}")
        
    elif res in {"fail", "cancel"}:
        order.status = "CANCELLED"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid result."
        )
        
    db.commit()
    db.refresh(order)
    return order

@router.get("/checkout/wompi-params/{order_number}", response_model=WompiParamsResponse)
def get_wompi_params(
    order_number: str,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.number == order_number,
        Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
        
    amount_in_cents = int(round(order.total * 100))
    currency = "COP"
    signature = WompiPaymentGateway.generate_integrity_signature(
        reference=order.number,
        amount_in_cents=amount_in_cents,
        currency=currency
    )
    
    # URL de retorno al frontend confirmación
    redirect_url = "http://localhost/payment/confirmation"
    
    return WompiParamsResponse(
        public_key=settings.WOMPI_PUBLIC_KEY,
        signature=signature,
        amount_in_cents=amount_in_cents,
        reference=order.number,
        currency=currency,
        redirect_url=redirect_url
    )

@router.post("/checkout/wompi-webhook")
def wompi_webhook(
    payload: dict,
    db: Session = Depends(get_db)
):
    # 1. Validar la firma criptográfica del Webhook
    if not WompiPaymentGateway.validate_webhook_signature(payload):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature."
        )
        
    event = payload.get("event")
    if event != "transaction.updated":
        return {"status": "ignored", "reason": "unsupported_event"}
        
    transaction_data = payload.get("data", {}).get("transaction", {})
    reference = transaction_data.get("reference")
    wompi_status = transaction_data.get("status")
    
    if not reference or not wompi_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing reference or status in transaction data."
        )
        
    order = db.query(Order).filter(Order.number == reference).first()
    if not order:
        logger.error(f"Webhook received for non-existent order: {reference}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
        
    if wompi_status == "APPROVED":
        if order.status == "PENDING":
            # Crear inscripciones basadas en OrderItems guardados de forma persistente
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            for item in order_items:
                existing = db.query(Enrollment).filter(
                    Enrollment.user_id == order.user_id,
                    Enrollment.course_id == item.course_id
                ).first()
                if not existing:
                    enrollment = Enrollment(
                        user_id=order.user_id,
                        course_id=item.course_id,
                        order_id=order.id,
                        status="ACTIVA"
                    )
                    db.add(enrollment)
            
            order.status = "CONFIRMED"
            # Limpiar carrito
            db.query(CartItem).filter(CartItem.user_id == order.user_id).delete()
            db.commit()
            logger.info(f"Order {reference} APPROVED and CONFIRMED via Wompi Webhook.")
            
            # Despachar tareas asíncronas de Celery y Eventos
            try:
                # 1. Email de confirmación al estudiante (cola high_priority)
                # Obtenemos email y nombre (simulado o a través del token)
                user_email = f"user{order.user_id}@skillforge.local" # Fallback temporal si no tenemos el user object
                user_name = "Estudiante"
                
                celery_app.send_task(
                    "shared.tasks.notifications.enviar_notificacion_orden_async",
                    kwargs={
                        "data": {
                            "email": user_email,
                            "nombre_usuario": user_name,
                            "numero_orden": order.number
                        }
                    },
                    queue="high_priority"
                )
                
                # 2. Publicar evento de orden completada
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../../"))
                from shared.event_bus import RedisEventBus
                
                bus = RedisEventBus()
                for item in order_items:
                    bus.publish(
                        stream="ordenes",
                        event_type="orden.completada",
                        data={
                            "user_id": order.user_id,
                            "course_id": item.course_id,
                            "order_number": order.number
                        }
                    )
            except Exception as e:
                logger.error(f"Error dispatching tasks/events on webhook approval: {str(e)}")
                
    elif wompi_status in {"DECLINED", "VOIDED", "ERROR"}:
        if order.status == "PENDING":
            order.status = "CANCELLED"
            db.commit()
            logger.warning(f"Order {reference} marked as CANCELLED due to Wompi status: {wompi_status}")
            
    return {"status": "processed", "order_status": order.status}

