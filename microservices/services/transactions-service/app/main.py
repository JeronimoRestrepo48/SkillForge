from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.models.course import CoursePrice
from app.models.cart import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.enrollment import Enrollment
from app.routers import cart, orders, enrollments, checkout

# Generate database tables
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        if db.query(CoursePrice).count() == 0:
            db.add_all([
                CoursePrice(course_id=1, title="Python Fundamentals", price=100.0),
                CoursePrice(course_id=2, title="Flask for APIs", price=120.0),
                CoursePrice(course_id=3, title="Arquitectura de Microservicios", price=150.0),
            ])
            db.flush()
            
            # Seed cart item and orders for user 1 (which matches standard test user)
            db.add(CartItem(user_id=1, course_id=1, quantity=1))
            
            order1 = Order(number="SF-10001", user_id=1, status="CONFIRMED", total=100.0)
            order2 = Order(number="SF-10002", user_id=1, status="PENDING", total=120.0)
            db.add_all([order1, order2])
            db.flush()
            
            db.add(OrderItem(order_id=order1.id, course_id=1, price=100.0, quantity=1))
            db.add(OrderItem(order_id=order2.id, course_id=2, price=120.0, quantity=1))
            
            # Seed active enrollment for Python Fundamentals
            db.add(Enrollment(user_id=1, course_id=1, order_id=order1.id, status="ACTIVA"))
            
            db.commit()
    finally:
        db.close()

seed_data()

app = FastAPI(title="SkillForge Transactions Service")

@app.get("/health")
def health():
    return {"status": "ok", "service": "transactions-service"}

# Standard API transactions endpoints
app.include_router(cart.router, prefix="/api/transactions", tags=["cart"])
app.include_router(orders.router, prefix="/api/transactions", tags=["orders"])
app.include_router(enrollments.router, prefix="/api/transactions", tags=["enrollments"])
app.include_router(checkout.router, prefix="/api/transactions", tags=["checkout"])

# Legacy API transactions endpoints for backwards compatibility/tests
app.include_router(cart.router, prefix="/api", tags=["legacy-cart"])
app.include_router(orders.router, prefix="/api", tags=["legacy-orders"])
app.include_router(enrollments.router, prefix="/api", tags=["legacy-enrollments"])
app.include_router(checkout.router, prefix="/api", tags=["legacy-checkout"])
