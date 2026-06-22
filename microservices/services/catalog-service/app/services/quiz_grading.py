from app.models.quiz import Quiz
from app.schemas.quiz import AnswerSubmit
from app.services.embeddings import get_embedding, cosine_similarity

def calificar_intento(quiz: Quiz, respuestas: list[AnswerSubmit]) -> dict:
    """
    Califica un intento de quiz basándose en las respuestas dadas.
    Retorna un diccionario con:
      - puntaje_obtenido
      - puntaje_maximo
      - porcentaje
      - aprobado
      - detalles_respuestas (lista con data para crear QuizAttemptAnswer)
    """
    puntaje_maximo = 0.0
    puntaje_obtenido = 0.0
    detalles = []

    # Crear mapa de preguntas para fácil acceso
    preguntas_map = {q.id: q for q in quiz.questions}

    for resp in respuestas:
        pregunta = preguntas_map.get(resp.question_id)
        if not pregunta:
            continue
            
        puntaje_maximo += pregunta.puntaje
        puntaje_pregunta = 0.0
        similitud = None

        if pregunta.tipo == "OPCION_MULTIPLE":
            # Buscar la opción seleccionada y verificar si es correcta
            opcion_correcta = next((opt for opt in pregunta.options if opt.es_correcta), None)
            if opcion_correcta and resp.selected_option_id == opcion_correcta.id:
                puntaje_pregunta = pregunta.puntaje
        
        elif pregunta.tipo == "ABIERTA":
            if resp.respuesta_texto and pregunta.respuesta_esperada_embedding:
                # Calcular embedding de la respuesta dada
                resp_embedding = get_embedding(resp.respuesta_texto)
                # Calcular similitud
                similitud = cosine_similarity(resp_embedding, pregunta.respuesta_esperada_embedding)
                
                # Asignar puntaje según rangos
                if similitud >= 0.75:
                    puntaje_pregunta = pregunta.puntaje
                elif similitud >= 0.60:
                    puntaje_pregunta = pregunta.puntaje * 0.70
                else:
                    puntaje_pregunta = 0.0

        puntaje_obtenido += puntaje_pregunta
        detalles.append({
            "question_id": pregunta.id,
            "respuesta_texto": resp.respuesta_texto,
            "selected_option_id": resp.selected_option_id,
            "similitud": similitud,
            "puntaje_obtenido": puntaje_pregunta
        })

    # Si el estudiante no respondió alguna pregunta, sumar al puntaje máximo de todas formas
    for q in quiz.questions:
        if not any(d["question_id"] == q.id for d in detalles):
            puntaje_maximo += q.puntaje

    porcentaje = (puntaje_obtenido / puntaje_maximo * 100.0) if puntaje_maximo > 0 else 0.0
    aprobado = porcentaje >= quiz.puntaje_minimo_aprobacion

    return {
        "puntaje_obtenido": puntaje_obtenido,
        "puntaje_maximo": puntaje_maximo,
        "porcentaje": porcentaje,
        "aprobado": aprobado,
        "detalles": detalles
    }
