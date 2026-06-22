from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.course import Course
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.rating import Rating
from app.schemas.catalog import CourseOut, CourseDetailOut, ModuleOut, ModuleWithLessons, CourseCreate, ModuleCreate, LessonCreate, LessonOut
from app.dependencies.auth import get_current_user, UserPayload

router = APIRouter()

@router.get("/courses")
def list_courses(
  q: Optional[str] = Query(None),
  categoria: Optional[int] = Query(None),
  page: int = Query(1, ge=1),
  page_size: int = Query(20, ge=1, le=100),
  db: Session = Depends(get_db)
):
  query = db.query(Course).filter(Course.status == "PUBLISHED")
  
  if q:
    query = query.filter(Course.title.ilike(f"%{q}%"))
  if categoria:
    query = query.filter(Course.category_id == categoria)
    
  query = query.order_by(Course.id.asc())
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
        "id": r.id,
        "title": r.title,
        "description": r.description,
        "category_id": r.category_id,
        "price": r.price,
        "status": r.status,
        "nivel_dificultad": r.nivel_dificultad,
        "duracion_horas": r.duracion_horas,
        "instructor_id": r.instructor_id
      } for r in results
    ]
  }

@router.post("/courses", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    if current_user.role not in ["instructor", "admin", "INSTRUCTOR", "ADMINISTRADOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors or administrators can create courses."
        )
    
    # Check if category exists
    from app.models.category import Category
    category = db.query(Category).filter(Category.id == course_in.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category_id."
        )
        
    new_course = Course(
        title=course_in.title,
        description=course_in.description,
        category_id=course_in.category_id,
        price=course_in.price,
        status=course_in.status,
        nivel_dificultad=course_in.nivel_dificultad,
        duracion_horas=course_in.duracion_horas,
        instructor_id=current_user.id,
        es_certificacion=course_in.es_certificacion
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/my-courses", response_model=List[CourseOut])
def get_my_courses(current_user: UserPayload = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["instructor", "admin", "INSTRUCTOR", "ADMINISTRADOR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(Course).filter(Course.instructor_id == current_user.id).all()

@router.get("/courses/{course_id}", response_model=CourseDetailOut)
def get_course_detail(course_id: int, db: Session = Depends(get_db)):
  course = db.query(Course).filter(Course.id == course_id, Course.status == "PUBLISHED").first()
  if not course:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Course not found."
    )
  
  modules = db.query(Module).filter(Module.course_id == course.id).order_by(Module.sort_order.asc()).all()
  
  rating_stats = db.query(
    func.count(Rating.id).label("count"),
    func.avg(Rating.score).label("average")
  ).filter(Rating.course_id == course.id).first()
  
  rating_count = rating_stats.count or 0
  average_rating = float(rating_stats.average or 0.0)
  
  return CourseDetailOut(
    id=course.id,
    title=course.title,
    description=course.description,
    category_id=course.category_id,
    price=course.price,
    status=course.status,
    nivel_dificultad=course.nivel_dificultad,
    duracion_horas=course.duracion_horas,
    instructor_id=course.instructor_id,
    modules=[ModuleWithLessons.from_orm(m) for m in modules],
    rating_count=rating_count,
    average_rating=average_rating
  )

@router.get("/courses/{course_id}/modules")
def get_course_modules(
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
    
  query = db.query(Module).filter(Module.course_id == course.id).order_by(Module.sort_order.asc())
  total = query.count()
  start = (page - 1) * page_size
  results = query.offset(start).limit(page_size).all()
  
  end = start + page_size
  return {
    "count": total,
    "next": page + 1 if end < total else None,
    "previous": page - 1 if page > 1 else None,
    "results": [ModuleOut.from_orm(m) for m in results]
  }

@router.put("/courses/{course_id}", response_model=CourseOut)
def update_course(
    course_id: int,
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != current_user.id and current_user.role not in ["admin", "ADMINISTRADOR"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit this course")
        
    for var, value in vars(course_in).items():
        setattr(course, var, value) if value is not None else None
        
    db.commit()
    db.refresh(course)
    return course

@router.post("/courses/{course_id}/modules", response_model=ModuleOut, status_code=status.HTTP_201_CREATED)
def create_module(
    course_id: int,
    module_in: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != current_user.id and current_user.role not in ["admin", "ADMINISTRADOR"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit this course")
        
    new_module = Module(
        course_id=course_id,
        title=module_in.title,
        sort_order=module_in.sort_order,
        es_examen_modulo=module_in.es_examen_modulo,
        es_examen_final=module_in.es_examen_final
    )
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    return new_module

@router.post("/modules/{module_id}/lessons", response_model=LessonOut, status_code=status.HTTP_201_CREATED)
def create_lesson(
    module_id: int,
    lesson_in: LessonCreate,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    course = db.query(Course).filter(Course.id == module.course_id).first()
    if not course or (course.instructor_id != current_user.id and current_user.role not in ["admin", "ADMINISTRADOR"]):
        raise HTTPException(status_code=403, detail="Not authorized to edit this course")
        
    new_lesson = Lesson(
        module_id=module_id,
        title=lesson_in.title,
        content_type=lesson_in.content_type,
        content=lesson_in.content,
        sort_order=lesson_in.sort_order,
        duration_minutes=lesson_in.duration_minutes
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson

@router.delete("/courses/{course_id}/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(
    course_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course or (course.instructor_id != current_user.id and current_user.role not in ["admin", "ADMINISTRADOR"]):
        raise HTTPException(status_code=403, detail="Not authorized to edit this course")
        
    module = db.query(Module).filter(Module.id == module_id, Module.course_id == course_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
        
    db.delete(module)
    db.commit()

@router.delete("/modules/{module_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    module_id: int,
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user)
):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    course = db.query(Course).filter(Course.id == module.course_id).first()
    if not course or (course.instructor_id != current_user.id and current_user.role not in ["admin", "ADMINISTRADOR"]):
        raise HTTPException(status_code=403, detail="Not authorized to edit this course")
        
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.module_id == module_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    db.delete(lesson)
    db.commit()
