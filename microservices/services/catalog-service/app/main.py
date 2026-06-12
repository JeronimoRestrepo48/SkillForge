from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.models.category import Category
from app.models.course import Course
from app.models.module import Module
from app.models.lesson import Lesson
from app.routers import courses, categories, modules, lessons, progress, wishlist, reviews

# Generate database tables
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        if db.query(Category).count() == 0:
            backend = Category(name="Backend")
            architecture = Category(name="Architecture")
            db.add_all([backend, architecture])
            db.flush()
            
            db.add_all([
                Course(
                    title="Python Fundamentals",
                    description="From zero to backend basics",
                    category_id=backend.id,
                    price=100.0,
                    status="PUBLISHED",
                    nivel_dificultad="PRINCIPIANTE",
                    duracion_horas=20,
                    instructor_id=2
                ),
                Course(
                    title="Flask for APIs",
                    description="Design and build production APIs",
                    category_id=backend.id,
                    price=120.0,
                    status="PUBLISHED",
                    nivel_dificultad="INTERMEDIO",
                    duracion_horas=25,
                    instructor_id=2
                ),
                Course(
                    title="Arquitectura de Microservicios",
                    description="Patterns for scalable systems",
                    category_id=architecture.id,
                    price=150.0,
                    status="PUBLISHED",
                    nivel_dificultad="AVANZADO",
                    duracion_horas=30,
                    instructor_id=2
                ),
            ])
            db.flush()
            
            all_courses = db.query(Course).all()
            for course in all_courses:
                m1 = Module(course_id=course.id, title=f"{course.title} - Module 1", sort_order=1)
                m2 = Module(course_id=course.id, title=f"{course.title} - Module 2", sort_order=2)
                db.add_all([m1, m2])
                db.flush()
                
                # Seed lessons for each module
                db.add_all([
                    Lesson(module_id=m1.id, title="Introducción", content_type="TEXTO", content="Texto de introducción", sort_order=1, duration_minutes=10),
                    Lesson(module_id=m1.id, title="Conceptos Clave", content_type="VIDEO", content="https://example.com/video1.mp4", sort_order=2, duration_minutes=20),
                    Lesson(module_id=m2.id, title="Práctica Guiada", content_type="PRACTICA", content="Instrucciones del laboratorio", sort_order=1, duration_minutes=30),
                    Lesson(module_id=m2.id, title="Quiz Final", content_type="QUIZ", content="Cuestionario de prueba", sort_order=2, duration_minutes=15),
                ])
            db.commit()
        else:
            # If categories exist, but lessons are missing, seed them for existing modules
            if db.query(Lesson).count() == 0:
                modules = db.query(Module).all()
                for mod in modules:
                    db.add_all([
                        Lesson(module_id=mod.id, title="Introducción", content_type="TEXTO", content="Texto de introducción", sort_order=1, duration_minutes=10),
                        Lesson(module_id=mod.id, title="Conceptos Clave", content_type="VIDEO", content="https://example.com/video1.mp4", sort_order=2, duration_minutes=20),
                        Lesson(module_id=mod.id, title="Práctica Guiada", content_type="PRACTICA", content="Instrucciones del laboratorio", sort_order=1, duration_minutes=30),
                        Lesson(module_id=mod.id, title="Quiz Final", content_type="QUIZ", content="Cuestionario de prueba", sort_order=2, duration_minutes=15),
                    ])
                db.commit()
    finally:
        db.close()

seed_data()

app = FastAPI(title="SkillForge Catalog Service")

@app.get("/health")
def health():
    return {"status": "ok", "service": "catalog-service"}

# Standard API catalog endpoints (with prefix)
app.include_router(courses.router, prefix="/api/catalog", tags=["courses"])
app.include_router(categories.router, prefix="/api/catalog", tags=["categories"])
app.include_router(modules.router, prefix="/api/catalog", tags=["modules"])
app.include_router(lessons.router, prefix="/api/catalog", tags=["lessons"])
app.include_router(progress.router, prefix="/api/catalog", tags=["progress"])
app.include_router(wishlist.router, prefix="/api/catalog", tags=["wishlist"])
app.include_router(reviews.router, prefix="/api/catalog", tags=["reviews"])

# Legacy API catalog endpoints (for backwards compatibility/tests)
app.include_router(courses.router, prefix="/api", tags=["legacy-courses"])
app.include_router(categories.router, prefix="/api", tags=["legacy-categories"])
app.include_router(modules.router, prefix="/api", tags=["legacy-modules"])
app.include_router(lessons.router, prefix="/api", tags=["legacy-lessons"])
app.include_router(progress.router, prefix="/api", tags=["legacy-progress"])
app.include_router(wishlist.router, prefix="/api", tags=["legacy-wishlist"])
app.include_router(reviews.router, prefix="/api", tags=["legacy-reviews"])
