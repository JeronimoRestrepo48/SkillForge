import os

from flask import Flask, jsonify, request
from sqlalchemy import Column, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

app = Flask(__name__)
Base = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///transactions.db")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


class CoursePrice(Base):
    __tablename__ = "course_prices"
    course_id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    price = Column(Float, nullable=False)


class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("course_prices.course_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    number = Column(String(40), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="PENDING")
    total = Column(Float, nullable=False, default=0)


def _seed_data():
    db = SessionLocal()
    try:
        if db.query(CoursePrice).count() == 0:
            db.add_all(
                [
                    CoursePrice(course_id=1, title="Python Fundamentals", price=100.0),
                    CoursePrice(course_id=2, title="Flask for APIs", price=120.0),
                    CoursePrice(course_id=3, title="Arquitectura de Microservicios", price=150.0),
                ]
            )
            db.flush()
            db.add(CartItem(user_id=1, course_id=1, quantity=1))
            db.add(Order(number="SF-10001", user_id=1, status="CONFIRMED", total=100.0))
            db.add(Order(number="SF-10002", user_id=1, status="PENDING", total=120.0))
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "transactions-service"})


@app.get("/api/orders")
def list_orders():
    user_id = int(request.headers.get("X-User-Id", request.args.get("user_id", "1")))
    db = SessionLocal()
    try:
        rows = db.query(Order).filter(Order.user_id == user_id).order_by(Order.id.desc()).all()
        result = [{"number": r.number, "user_id": r.user_id, "status": r.status, "total": r.total} for r in rows]
        return jsonify({"count": len(result), "results": result})
    finally:
        db.close()


@app.get("/api/cart")
def get_cart():
    user_id = int(request.headers.get("X-User-Id", request.args.get("user_id", "1")))
    db = SessionLocal()
    try:
        items = db.query(CartItem).filter(CartItem.user_id == user_id).order_by(CartItem.id.asc()).all()
        detailed = []
        total = 0.0
        for item in items:
            course = db.query(CoursePrice).filter(CoursePrice.course_id == item.course_id).first()
            if not course:
                continue
            subtotal = course.price * item.quantity
            total += subtotal
            detailed.append(
                {
                    "course_id": item.course_id,
                    "course_title": course.title,
                    "quantity": item.quantity,
                    "unit_price": course.price,
                    "subtotal": round(subtotal, 2),
                }
            )
        return jsonify({"count": len(detailed), "results": detailed, "total": round(total, 2)})
    finally:
        db.close()


@app.post("/api/cart/add")
def add_to_cart():
    payload = request.get_json(silent=True) or {}
    user_id = int(request.headers.get("X-User-Id", payload.get("user_id", 1)))
    course_id = int(payload.get("course_id", 0))
    quantity = int(payload.get("quantity", 1))
    if quantity < 1:
        return jsonify({"detail": "Quantity must be at least 1."}), 400
    db = SessionLocal()
    try:
        course = db.query(CoursePrice).filter(CoursePrice.course_id == course_id).first()
        if not course:
            return jsonify({"detail": "Course not found."}), 404
        existing = db.query(CartItem).filter(CartItem.user_id == user_id, CartItem.course_id == course_id).first()
        if existing:
            existing.quantity += quantity
        else:
            db.add(CartItem(user_id=user_id, course_id=course_id, quantity=quantity))
        db.commit()
        return jsonify({"detail": "Course added to cart."}), 201
    finally:
        db.close()


@app.post("/api/cart/remove")
def remove_from_cart():
    payload = request.get_json(silent=True) or {}
    user_id = int(request.headers.get("X-User-Id", payload.get("user_id", 1)))
    course_id = int(payload.get("course_id", 0))
    db = SessionLocal()
    try:
        item = db.query(CartItem).filter(CartItem.user_id == user_id, CartItem.course_id == course_id).first()
        if not item:
            return jsonify({"detail": "Course not in cart."}), 404
        db.delete(item)
        db.commit()
        return jsonify({"detail": "Course removed from cart."})
    finally:
        db.close()


@app.post("/api/checkout/confirm")
def checkout_confirm():
    payload = request.get_json(silent=True) or {}
    user_id = int(request.headers.get("X-User-Id", payload.get("user_id", 1)))
    db = SessionLocal()
    try:
        cart = db.query(CartItem).filter(CartItem.user_id == user_id).all()
        if not cart:
            return jsonify({"detail": "Your cart is empty."}), 400
        total = 0.0
        for item in cart:
            course = db.query(CoursePrice).filter(CoursePrice.course_id == item.course_id).first()
            if course:
                total += course.price * item.quantity
        next_id = (db.query(Order.id).order_by(Order.id.desc()).first() or [0])[0] + 1
        number = f"SF-{10000 + next_id}"
        row = Order(number=number, user_id=user_id, status="PENDING", total=round(total, 2))
        db.add(row)
        db.commit()
        db.refresh(row)
        return jsonify({"number": row.number, "user_id": row.user_id, "status": row.status, "total": row.total}), 201
    finally:
        db.close()


@app.post("/api/checkout/return")
def checkout_return():
    payload = request.get_json(silent=True) or {}
    user_id = int(request.headers.get("X-User-Id", payload.get("user_id", 1)))
    number = payload.get("order_number", "")
    result = payload.get("result", "success").lower()
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.number == number, Order.user_id == user_id).first()
        if not order:
            return jsonify({"detail": "Order not found."}), 404
        if result == "success":
            order.status = "CONFIRMED"
            db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        elif result in {"fail", "cancel"}:
            order.status = "CANCELLED"
        else:
            return jsonify({"detail": "Invalid result."}), 400
        db.commit()
        return jsonify({"number": order.number, "user_id": order.user_id, "status": order.status, "total": order.total})
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
_seed_data()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
