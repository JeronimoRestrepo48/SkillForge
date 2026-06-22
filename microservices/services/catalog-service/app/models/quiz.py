from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, unique=True, index=True)
    titulo = Column(String(200), nullable=False)
    puntaje_minimo_aprobacion = Column(Float, nullable=False, default=60.0)
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.sort_order")
    # Para acceder al lesson original si lo necesitamos
    # lesson = relationship("Lesson", back_populates="quiz") # Asumiendo que no tocamos Lesson, lo dejamos sin back_populates

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    tipo = Column(String(20), nullable=False)  # OPCION_MULTIPLE, ABIERTA
    enunciado = Column(Text, nullable=False)
    puntaje = Column(Float, nullable=False, default=1.0)
    sort_order = Column(Integer, nullable=False, default=1)
    respuesta_esperada = Column(Text, nullable=True)  # solo ABIERTA
    respuesta_esperada_embedding = Column(JSON, nullable=True)  # solo ABIERTA
    
    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("QuizOption", back_populates="question", cascade="all, delete-orphan")

class QuizOption(Base):
    __tablename__ = "quiz_options"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False, index=True)
    texto = Column(String(500), nullable=False)
    es_correcta = Column(Boolean, nullable=False, default=False)
    
    question = relationship("QuizQuestion", back_populates="options")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    puntaje_obtenido = Column(Float, nullable=False, default=0.0)
    puntaje_maximo = Column(Float, nullable=False, default=0.0)
    porcentaje = Column(Float, nullable=False, default=0.0)
    aprobado = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    answers = relationship("QuizAttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")

class QuizAttemptAnswer(Base):
    __tablename__ = "quiz_attempt_answers"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False, index=True)
    respuesta_texto = Column(Text, nullable=True)  # ABIERTA
    selected_option_id = Column(Integer, ForeignKey("quiz_options.id"), nullable=True)  # OPCION_MULTIPLE
    similitud = Column(Float, nullable=True)  # solo ABIERTA
    puntaje_obtenido = Column(Float, nullable=False, default=0.0)
    
    attempt = relationship("QuizAttempt", back_populates="answers")
