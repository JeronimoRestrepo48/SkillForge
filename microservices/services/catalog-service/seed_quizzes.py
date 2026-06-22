from app.database import SessionLocal
from app.models.lesson import Lesson
from app.models.quiz import Quiz, QuizQuestion, QuizOption
from sqlalchemy.orm import Session

db = SessionLocal()
lessons = db.query(Lesson).filter(Lesson.content_type == "QUIZ").all()

for lesson in lessons:
    quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson.id).first()
    if not quiz:
        print(f"Adding quiz to lesson {lesson.id}...")
        new_quiz = Quiz(
            lesson_id=lesson.id,
            titulo=f"Quiz para la lección {lesson.title}",
            puntaje_minimo_aprobacion=70.0
        )
        db.add(new_quiz)
        db.flush()
        
        # Add questions
        q1 = QuizQuestion(
            quiz_id=new_quiz.id,
            enunciado="¿Cuál de las siguientes afirmaciones es verdadera en este contexto?",
            tipo="OPCION_MULTIPLE",
            puntaje=1.0,
            sort_order=1
        )
        db.add(q1)
        db.flush()
        
        o1 = QuizOption(question_id=q1.id, texto="Opción A (Falsa)", es_correcta=False)
        o2 = QuizOption(question_id=q1.id, texto="Opción B (Verdadera)", es_correcta=True)
        o3 = QuizOption(question_id=q1.id, texto="Opción C (Falsa)", es_correcta=False)
        db.add_all([o1, o2, o3])
        
        q2 = QuizQuestion(
            quiz_id=new_quiz.id,
            enunciado="El patrón de diseño Singleton permite instanciar una clase múltiples veces.",
            tipo="OPCION_MULTIPLE",
            puntaje=1.0,
            sort_order=2
        )
        db.add(q2)
        db.flush()
        
        o4 = QuizOption(question_id=q2.id, texto="Verdadero", es_correcta=False)
        o5 = QuizOption(question_id=q2.id, texto="Falso", es_correcta=True)
        db.add_all([o4, o5])
        
db.commit()
print("Done!")
