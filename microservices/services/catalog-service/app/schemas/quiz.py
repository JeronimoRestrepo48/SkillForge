from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class QuizOptionBase(BaseModel):
    texto: str
    es_correcta: bool = False

class QuizOptionCreate(QuizOptionBase):
    pass

class QuizOptionOut(BaseModel):
    id: int
    texto: str
    
    class Config:
        from_attributes = True

class QuizOptionInstructorOut(QuizOptionOut):
    es_correcta: bool

class QuizQuestionBase(BaseModel):
    tipo: str  # OPCION_MULTIPLE o ABIERTA
    enunciado: str
    puntaje: float = 1.0
    sort_order: int = 1
    respuesta_esperada: Optional[str] = None

class QuizQuestionCreate(QuizQuestionBase):
    options: Optional[List[QuizOptionCreate]] = []

class QuizQuestionStudentOut(BaseModel):
    id: int
    tipo: str
    enunciado: str
    puntaje: float
    sort_order: int
    options: List[QuizOptionOut] = []

    class Config:
        from_attributes = True

class QuizQuestionOut(QuizQuestionStudentOut):
    respuesta_esperada: Optional[str] = None
    options: List[QuizOptionInstructorOut] = []

class QuizBase(BaseModel):
    titulo: str
    puntaje_minimo_aprobacion: float = 60.0

class QuizCreate(QuizBase):
    lesson_id: int
    questions: List[QuizQuestionCreate]

class QuizOut(QuizBase):
    id: int
    lesson_id: int
    
    class Config:
        from_attributes = True

class QuizDetailOut(QuizOut):
    questions: List[QuizQuestionStudentOut] = []

class QuizDetailInstructorOut(QuizOut):
    questions: List[QuizQuestionOut] = []

# --- Attempts ---

class AnswerSubmit(BaseModel):
    question_id: int
    respuesta_texto: Optional[str] = None
    selected_option_id: Optional[int] = None

class QuizAttemptSubmit(BaseModel):
    respuestas: List[AnswerSubmit]

class QuizAttemptAnswerOut(BaseModel):
    id: int
    question_id: int
    respuesta_texto: Optional[str]
    selected_option_id: Optional[int]
    similitud: Optional[float]
    puntaje_obtenido: float
    
    class Config:
        from_attributes = True

class QuizAttemptResultOut(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    puntaje_obtenido: float
    puntaje_maximo: float
    porcentaje: float
    aprobado: bool
    created_at: datetime
    answers: List[QuizAttemptAnswerOut] = []

    class Config:
        from_attributes = True
