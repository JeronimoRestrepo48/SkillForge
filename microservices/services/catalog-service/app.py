import os

from flask import Flask, jsonify, request
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, scoped_session, sessionmaker

app = Flask(__name__)
Base = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///catalog.db")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="PUBLISHED")
    category = relationship("Category")


class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    sort_order = Column(Integer, nullable=False, default=1)


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    score = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False, default="")


def _seed_data():
    db = SessionLocal()
    try:
        if db.query(Category).count() == 0:
            backend = Category(name="Backend")
            architecture = Category(name="Architecture")
            db.add_all([backend, architecture])
            db.flush()
            db.add_all(
                [
                    Course(
                        title="Python Fundamentals",
                        description="From zero to backend basics",
                        category_id=backend.id,
                        price=100.0,
                        status="PUBLISHED",
                    ),
                    Course(
                        title="Flask for APIs",
                        description="Design and build production APIs",
                        category_id=backend.id,
                        price=120.0,
                        status="PUBLISHED",
                    ),
                    Course(
                        title="Arquitectura de Microservicios",
                        description="Patterns for scalable systems",
                        category_id=architecture.id,
                        price=150.0,
                        status="PUBLISHED",
                    ),
                ]
            )
            db.flush()
            all_courses = db.query(Course).all()
            for course in all_courses:
                db.add(Module(course_id=course.id, title=f"{course.title} - Module 1", sort_order=1))
                db.add(Module(course_id=course.id, title=f"{course.title} - Module 2", sort_order=2))
            db.commit()
    finally:
        db.close()


def paginate(items):
    page = max(1, int(request.args.get("page", "1")))
    page_size = min(100, max(1, int(request.args.get("page_size", "20"))))
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "count": total,
        "next": page + 1 if end < total else None,
        "previous": page - 1 if page > 1 else None,
        "results": items[start:end],
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "catalog-service"})


@app.get("/api/courses")
def courses():
    q = request.args.get("q", "").strip().lower()
    category_id = request.args.get("categoria")
    db = SessionLocal()
    try:
        query = db.query(Course).filter(Course.status == "PUBLISHED")
        if q:
            query = query.filter(Course.title.ilike(f"%{q}%"))
        if category_id and category_id.isdigit():
            query = query.filter(Course.category_id == int(category_id))
        rows = [
            {
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "category_id": row.category_id,
                "price": row.price,
                "status": row.status,
            }
            for row in query.order_by(Course.id.asc()).all()
        ]
        return jsonify(paginate(rows))
    finally:
        db.close()


@app.get("/api/courses/<int:course_id>")
def course_detail(course_id: int):
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.id == course_id, Course.status == "PUBLISHED").first()
        if not course:
            return jsonify({"detail": "Course not found."}), 404
        modules = db.query(Module).filter(Module.course_id == course.id).order_by(Module.sort_order.asc()).all()
        rating_count = db.query(Rating).filter(Rating.course_id == course.id).count()
        return jsonify(
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "category_id": course.category_id,
                "price": course.price,
                "status": course.status,
                "modules": [{"id": m.id, "title": m.title, "order": m.sort_order} for m in modules],
                "rating_count": rating_count,
            }
        )
    finally:
        db.close()


@app.get("/api/courses/<int:course_id>/modules")
def course_modules(course_id: int):
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.id == course_id, Course.status == "PUBLISHED").first()
        if not course:
            return jsonify({"detail": "Course not found."}), 404
        rows = [
            {"id": m.id, "title": m.title, "order": m.sort_order}
            for m in db.query(Module).filter(Module.course_id == course.id).order_by(Module.sort_order.asc()).all()
        ]
        return jsonify(paginate(rows))
    finally:
        db.close()


@app.get("/api/categories")
def categories():
    db = SessionLocal()
    try:
        rows = [{"id": row.id, "name": row.name} for row in db.query(Category).order_by(Category.id.asc()).all()]
        return jsonify(paginate(rows))
    finally:
        db.close()


@app.post("/api/courses/<int:course_id>/rate")
def course_rate(course_id: int):
    payload = request.get_json(silent=True) or {}
    user_id = int(request.headers.get("X-User-Id", payload.get("user_id", 0) or 0))
    score = payload.get("puntuacion")
    comment = payload.get("comentario", "")
    if not isinstance(score, int) or score < 1 or score > 5:
        return jsonify({"detail": "Invalid rating data."}), 400
    if user_id <= 0:
        return jsonify({"detail": "Authentication required"}), 401
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.id == course_id, Course.status == "PUBLISHED").first()
        if not course:
            return jsonify({"detail": "Course not found."}), 404
        row = Rating(course_id=course.id, user_id=user_id, score=score, comment=str(comment))
        db.add(row)
        db.commit()
        db.refresh(row)
        return jsonify({"id": row.id, "curso_id": course.id, "puntuacion": row.score, "comentario": row.comment}), 201
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
_seed_data()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
