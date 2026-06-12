from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class LessonBase(BaseModel):
    title: str
    content_type: str = "TEXTO"
    content: Optional[str] = None
    sort_order: int = 1
    duration_minutes: int = 0

class LessonCreate(LessonBase):
    pass

class LessonOut(LessonBase):
    id: int
    module_id: int

    class Config:
        from_attributes = True

class ModuleBase(BaseModel):
    title: str
    sort_order: int = 1

class ModuleCreate(ModuleBase):
    pass

class ModuleOut(ModuleBase):
    id: int
    course_id: int

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    description: str
    category_id: int
    price: float
    status: str = "PUBLISHED"
    nivel_dificultad: str = "PRINCIPIANTE"
    duracion_horas: int = 0

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int
    instructor_id: int

    class Config:
        from_attributes = True

class ModuleWithLessons(ModuleOut):
    lessons: List[LessonOut] = []

    class Config:
        from_attributes = True

class CourseDetailOut(CourseOut):
    modules: List[ModuleWithLessons] = []
    rating_count: int = 0
    average_rating: float = 0.0

    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    score: int = Field(..., ge=1, le=5)
    comment: str = ""

class RatingCreate(RatingBase):
    pass

class RatingOut(RatingBase):
    id: int
    course_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class WishlistCreate(BaseModel):
    course_id: int

class WishlistItemOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    added_at: datetime
    course: Optional[CourseOut] = None

    class Config:
        from_attributes = True

class LessonProgressOut(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    completed: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CourseProgressOut(BaseModel):
    course_id: int
    total_lessons: int
    completed_lessons: int
    percentage: float
    completed: bool
    completed_lesson_ids: List[int] = []
