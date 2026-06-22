from sqlalchemy.orm import Session
from app.models.course import Course
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.quiz import Quiz, QuizAttempt
from app.models.progress import LessonProgress
import logging

logger = logging.getLogger(__name__)

def get_module_status(db: Session, user_id: int, course: Course) -> list[dict]:
    """
    Retorna, para cada módulo del curso (ordenado por sort_order), un dict:
    { module_id, title, sort_order, es_examen_modulo, es_examen_final,
      bloqueado: bool, aprobado: bool (si tiene examen y fue aprobado, None si no aplica) }
    """
    # 1. Obtener módulos ordenados
    modules = db.query(Module).filter(Module.course_id == course.id).order_by(Module.sort_order.asc()).all()
    if not modules:
        return []

    # 2. Cargar lecciones, quizzes e intentos
    module_ids = [m.id for m in modules]
    lessons = db.query(Lesson).filter(Lesson.module_id.in_(module_ids)).all()
    lesson_ids = [l.id for l in lessons]

    quizzes = db.query(Quiz).filter(Quiz.lesson_id.in_(lesson_ids)).all()
    quiz_by_lesson_id = {q.lesson_id: q for q in quizzes}

    # Intentos aprobados del usuario
    quiz_ids = [q.id for q in quizzes]
    approved_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.quiz_id.in_(quiz_ids),
        QuizAttempt.aprobado == True
    ).all()
    approved_quiz_ids = {a.quiz_id for a in approved_attempts}

    # Lecciones completadas del usuario
    completed_progress = db.query(LessonProgress).filter(
        LessonProgress.user_id == user_id,
        LessonProgress.lesson_id.in_(lesson_ids),
        LessonProgress.completed == True
    ).all()
    completed_lesson_ids = {p.lesson_id for p in completed_progress}

    # 3. Evaluar estado secuencial
    result = []
    
    # El primer módulo siempre está desbloqueado
    prev_module_completed = True

    for i, module in enumerate(modules):
        bloqueado = not prev_module_completed if i > 0 else False

        # Determinar si este módulo está aprobado o completado
        module_lessons = [l for l in lessons if l.module_id == module.id]
        
        aprobado = None
        is_completed = False

        if module.es_examen_modulo or module.es_examen_final:
            # Buscar el quiz del módulo
            module_quizzes = [quiz_by_lesson_id[l.id] for l in module_lessons if l.id in quiz_by_lesson_id]
            if not module_quizzes:
                logger.warning(f"Módulo {module.id} es examen pero no tiene quiz asociado. Desbloqueo por defecto.")
                aprobado = True
                is_completed = True
            else:
                # Asumimos que hay un quiz principal por módulo de examen
                quiz = module_quizzes[0]
                aprobado = quiz.id in approved_quiz_ids
                is_completed = aprobado
        else:
            # Módulo normal: está completado si TODAS sus lecciones están completadas
            if not module_lessons:
                is_completed = True # Módulo sin lecciones
            else:
                is_completed = all(l.id in completed_lesson_ids for l in module_lessons)

        result.append({
            "module_id": module.id,
            "title": module.title,
            "sort_order": module.sort_order,
            "es_examen_modulo": module.es_examen_modulo,
            "es_examen_final": module.es_examen_final,
            "bloqueado": bloqueado,
            "aprobado": aprobado
        })

        # Para el siguiente módulo en la iteración
        prev_module_completed = is_completed

    return result
