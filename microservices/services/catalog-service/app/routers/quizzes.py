from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user, UserPayload
from app.models.lesson import Lesson
from app.models.quiz import Quiz, QuizQuestion, QuizOption, QuizAttempt, QuizAttemptAnswer
from app.schemas.quiz import (
    QuizCreate, QuizDetailOut, QuizDetailInstructorOut, 
    QuizAttemptSubmit, QuizAttemptResultOut
)
from app.services.embeddings import get_embedding
from app.services.quiz_grading import calificar_intento
from app.models.course import Course
from app.models.module import Module

router = APIRouter()

@router.post("/lessons/{lesson_id}/quiz", response_model=QuizDetailInstructorOut)
def create_quiz(lesson_id: int, payload: QuizCreate, db: Session = Depends(get_db), current_user: UserPayload = Depends(get_current_user)):
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    if lesson.content_type != "QUIZ":
        raise HTTPException(status_code=400, detail="Lesson content_type must be QUIZ")

    existing_quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson_id).first()
    if existing_quiz:
        raise HTTPException(status_code=400, detail="Lesson already has a quiz")

    quiz = Quiz(
        lesson_id=lesson_id,
        titulo=payload.titulo,
        puntaje_minimo_aprobacion=payload.puntaje_minimo_aprobacion
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    for q_data in payload.questions:
        q_embedding = None
        if q_data.tipo == "ABIERTA" and q_data.respuesta_esperada:
            q_embedding = get_embedding(q_data.respuesta_esperada)
            
        question = QuizQuestion(
            quiz_id=quiz.id,
            tipo=q_data.tipo,
            enunciado=q_data.enunciado,
            puntaje=q_data.puntaje,
            sort_order=q_data.sort_order,
            respuesta_esperada=q_data.respuesta_esperada,
            respuesta_esperada_embedding=q_embedding
        )
        db.add(question)
        db.commit()
        db.refresh(question)

        if q_data.options:
            for opt_data in q_data.options:
                option = QuizOption(
                    question_id=question.id,
                    texto=opt_data.texto,
                    es_correcta=opt_data.es_correcta
                )
                db.add(option)
            db.commit()

    db.refresh(quiz)
    return quiz

@router.get("/lessons/{lesson_id}/quiz", response_model=QuizDetailOut)
def get_quiz_student(lesson_id: int, db: Session = Depends(get_db), current_user: UserPayload = Depends(get_current_user)):
    quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.get("/lessons/{lesson_id}/quiz/instructor", response_model=QuizDetailInstructorOut)
def get_quiz_instructor(lesson_id: int, db: Session = Depends(get_db), current_user: UserPayload = Depends(get_current_user)):
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.put("/quizzes/{quiz_id}", response_model=QuizDetailInstructorOut)
def update_quiz(quiz_id: int, payload: QuizCreate, db: Session = Depends(get_db), current_user: UserPayload = Depends(get_current_user)):
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    quiz.titulo = payload.titulo
    quiz.puntaje_minimo_aprobacion = payload.puntaje_minimo_aprobacion
    
    # Simple approach: delete existing questions and recreate
    # (A proper approach would diff them, but for brevity we replace them)
    db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).delete()
    
    for q_data in payload.questions:
        q_embedding = None
        if q_data.tipo == "ABIERTA" and q_data.respuesta_esperada:
            q_embedding = get_embedding(q_data.respuesta_esperada)
            
        question = QuizQuestion(
            quiz_id=quiz.id,
            tipo=q_data.tipo,
            enunciado=q_data.enunciado,
            puntaje=q_data.puntaje,
            sort_order=q_data.sort_order,
            respuesta_esperada=q_data.respuesta_esperada,
            respuesta_esperada_embedding=q_embedding
        )
        db.add(question)
        db.commit()
        db.refresh(question)

        if q_data.options:
            for opt_data in q_data.options:
                option = QuizOption(
                    question_id=question.id,
                    texto=opt_data.texto,
                    es_correcta=opt_data.es_correcta
                )
                db.add(option)
            db.commit()

    db.refresh(quiz)
    return quiz

@router.post("/quizzes/{quiz_id}/attempts", response_model=QuizAttemptResultOut)
def submit_quiz_attempt(quiz_id: int, payload: QuizAttemptSubmit, db: Session = Depends(get_db), current_user: UserPayload = Depends(get_current_user)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    course = db.query(Course).join(Module).join(Lesson).filter(Lesson.id == quiz.lesson_id).first()
    if course and course.es_certificacion:
        from app.services.certification_progress import get_module_status
        module_status = get_module_status(db, current_user.id, course)
        lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()
        modulo_actual = next((m for m in module_status if m["module_id"] == lesson.module_id), None)
        if modulo_actual and modulo_actual.get("bloqueado"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Debes aprobar el examen del módulo anterior para acceder a este quiz."
            )

    resultado = calificar_intento(quiz, payload.respuestas)
    
    attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=current_user.id,
        puntaje_obtenido=resultado["puntaje_obtenido"],
        puntaje_maximo=resultado["puntaje_maximo"],
        porcentaje=resultado["porcentaje"],
        aprobado=resultado["aprobado"]
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    for det in resultado["detalles"]:
        answer = QuizAttemptAnswer(
            attempt_id=attempt.id,
            question_id=det["question_id"],
            respuesta_texto=det["respuesta_texto"],
            selected_option_id=det["selected_option_id"],
            similitud=det["similitud"],
            puntaje_obtenido=det["puntaje_obtenido"]
        )
        db.add(answer)
    
    if attempt.aprobado:
        from app.models.progress import LessonProgress
        progress = db.query(LessonProgress).filter(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == quiz.lesson_id
        ).first()
        if not progress:
            progress = LessonProgress(
                user_id=current_user.id,
                lesson_id=quiz.lesson_id,
                completed=True
            )
            db.add(progress)
        else:
            progress.completed = True
    
    db.commit()
    db.refresh(attempt)
    return attempt

@router.get("/quizzes/{quiz_id}/attempts/me", response_model=list[QuizAttemptResultOut])
def get_my_attempts(quiz_id: int, db: Session = Depends(get_db), current_user: UserPayload = Depends(get_current_user)):
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.user_id == current_user.id
    ).order_by(QuizAttempt.created_at.desc()).all()
    return attempts
