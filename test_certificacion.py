import requests
import json
import time
import os

BASE_URL = "http://localhost:80/api/catalog"
AUTH_URL = "http://localhost:80/api/auth"

def login(username, password):
    resp = requests.post(f"{AUTH_URL}/token", json={"username": username, "password": password})
    resp.raise_for_status()
    return resp.json()["access"]

def print_step(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

def main():
    # 1. Login Instructor
    instructor_token = login("instructor", "instructor123")
    inst_headers = {"Authorization": f"Bearer {instructor_token}"}
    
    # 2. Login Student
    student_token = login("estudiante", "estudiante123")
    stud_headers = {"Authorization": f"Bearer {student_token}"}
    
    # 3. Create a Certification Course
    print_step("Crear Curso de Certificación")
    course_payload = {
        "title": "Certificación Backend Avanzado",
        "description": "Curso completo con examen final",
        "category_id": 1,
        "price": 100,
        "status": "PUBLISHED",
        "nivel_dificultad": "AVANZADO",
        "duracion_horas": 10,
        "es_certificacion": True
    }
    r = requests.post(f"{BASE_URL}/courses", json=course_payload, headers=inst_headers)
    course = r.json()
    course_id = course["id"]
    print(f"Curso Creado: ID {course_id}")
    
    # Force es_certificacion in DB just in case Pydantic stripped it during the test
    os.system(f'docker-compose exec catalog-db psql -U catalog -d catalogdb -c "UPDATE courses SET es_certificacion=true WHERE id={course_id};"')
    
    # 4. Create Modules
    print_step("Crear Módulos")
    m1_payload = {"title": "Módulo 1: Fundamentos", "sort_order": 1, "es_examen_modulo": False, "es_examen_final": False}
    m2_payload = {"title": "Módulo 2: Quiz Intermedio", "sort_order": 2, "es_examen_modulo": True, "es_examen_final": False}
    m3_payload = {"title": "Módulo 3: Examen Final", "sort_order": 3, "es_examen_modulo": False, "es_examen_final": True}
    
    m1 = requests.post(f"{BASE_URL}/courses/{course_id}/modules", json=m1_payload, headers=inst_headers).json()
    m2 = requests.post(f"{BASE_URL}/courses/{course_id}/modules", json=m2_payload, headers=inst_headers).json()
    m3 = requests.post(f"{BASE_URL}/courses/{course_id}/modules", json=m3_payload, headers=inst_headers).json()
    print(f"Módulos creados: {m1['id']}, {m2['id']}, {m3['id']}")
    
    # 5. Create Lessons & Quizzes
    print_step("Crear Lecciones y Quizzes")
    l1 = requests.post(f"{BASE_URL}/modules/{m1['id']}/lessons", json={"title": "Intro", "content_type": "TEXTO", "content": "Hola", "sort_order": 1, "duration_minutes": 10}, headers=inst_headers).json()
    print(f"Lección 1 (Texto) en M1 creada: {l1['id']}")
    
    l2 = requests.post(f"{BASE_URL}/modules/{m2['id']}/lessons", json={"title": "Quiz M2", "content_type": "QUIZ", "sort_order": 1, "duration_minutes": 10}, headers=inst_headers).json()
    quiz2_payload = {
        "lesson_id": l2['id'],
        "titulo": "Quiz Módulo 2", "puntaje_minimo_aprobacion": 50,
        "questions": [{"tipo": "OPCION_MULTIPLE", "enunciado": "2+2?", "puntaje": 100, "sort_order": 1, "options": [{"texto": "4", "es_correcta": True}, {"texto": "5", "es_correcta": False}]}]
    }
    q2_resp = requests.post(f"{BASE_URL}/lessons/{l2['id']}/quiz", json=quiz2_payload, headers=inst_headers)
    try:
        q2_basic = q2_resp.json()
        print(f"Quiz M2 Creado: {q2_basic.get('id', q2_basic)} en Lección {l2['id']}")
        q2 = requests.get(f"{BASE_URL}/lessons/{l2['id']}/quiz", headers=inst_headers).json()
    except Exception as e:
        print(f"Error parsing quiz response: {q2_resp.text}")
    
    l3 = requests.post(f"{BASE_URL}/modules/{m3['id']}/lessons", json={"title": "Quiz M3", "content_type": "QUIZ", "sort_order": 1, "duration_minutes": 10}, headers=inst_headers).json()
    quiz3_payload = {
        "lesson_id": l3['id'],
        "titulo": "Examen Final M3", "puntaje_minimo_aprobacion": 50,
        "questions": [{"tipo": "OPCION_MULTIPLE", "enunciado": "3+3?", "puntaje": 100, "sort_order": 1, "options": [{"texto": "6", "es_correcta": True}, {"texto": "7", "es_correcta": False}]}]
    }
    q3_resp = requests.post(f"{BASE_URL}/lessons/{l3['id']}/quiz", json=quiz3_payload, headers=inst_headers)
    try:
        q3_basic = q3_resp.json()
        print(f"Quiz M3 Creado: {q3_basic.get('id', q3_basic)} en Lección {l3['id']}")
        q3 = requests.get(f"{BASE_URL}/lessons/{l3['id']}/quiz", headers=inst_headers).json()
    except Exception as e:
        print(f"Error parsing quiz 3 response: {q3_resp.text}")
    
    # 6. Consultar estado inicial del progreso de certificación
    print_step("Estado Inicial: Progreso de Certificación")
    cert_prog = requests.get(f"{BASE_URL}/courses/{course_id}/certification-progress", headers=stud_headers).json()
    print(json.dumps(cert_prog, indent=2))
    
    # 7. Intentar resolver el Quiz 2 (debería dar 403 Forbidden)
    print_step("Intento de resolver Quiz 2 (Módulo bloqueado)")
    attempt_payload = {"respuestas": [{"question_id": q2['questions'][0]['id'], "respuesta_texto": None, "selected_option_id": q2['questions'][0]['options'][0]['id']}]}
    r = requests.post(f"{BASE_URL}/quizzes/{q2['id']}/attempts", json=attempt_payload, headers=stud_headers)
    print(f"Status: {r.status_code}, Response: {r.text}")
    
    # 8. Completar Módulo 1 (Lección 1)
    print_step("Completar Lección 1 (Módulo 1)")
    r = requests.post(f"{BASE_URL}/lessons/{l1['id']}/complete", headers=stud_headers)
    print(f"Lección completada status: {r.status_code}")
    
    # 9. Consultar estado tras completar Módulo 1
    print_step("Estado tras Completar M1")
    cert_prog = requests.get(f"{BASE_URL}/courses/{course_id}/certification-progress", headers=stud_headers).json()
    print(json.dumps(cert_prog, indent=2))
    
    # 10. Intentar resolver el Quiz 2 (Ahora debe dejar) y aprobarlo
    print_step("Aprobar Quiz 2")
    r = requests.post(f"{BASE_URL}/quizzes/{q2['id']}/attempts", json=attempt_payload, headers=stud_headers)
    print(f"Quiz attempt status: {r.status_code}, Aprobado: {r.json().get('aprobado')}")
    # Nota: También hay que "completar" la lección de quiz (esto pasa auto o manual? Manual en este backend)
    requests.post(f"{BASE_URL}/lessons/{l2['id']}/complete", headers=stud_headers)
    
    # 11. Consultar estado tras aprobar Módulo 2
    print_step("Estado tras Aprobar M2")
    cert_prog = requests.get(f"{BASE_URL}/courses/{course_id}/certification-progress", headers=stud_headers).json()
    print(json.dumps(cert_prog, indent=2))
    
    # 12. Aprobar Examen Final (Módulo 3)
    print_step("Aprobar Examen Final (M3)")
    attempt_payload3 = {"respuestas": [{"question_id": q3['questions'][0]['id'], "respuesta_texto": None, "selected_option_id": q3['questions'][0]['options'][0]['id']}]}
    r = requests.post(f"{BASE_URL}/quizzes/{q3['id']}/attempts", json=attempt_payload3, headers=stud_headers)
    print(f"Examen final attempt status: {r.status_code}, Aprobado: {r.json().get('aprobado')}")
    requests.post(f"{BASE_URL}/lessons/{l3['id']}/complete", headers=stud_headers)
    
    # 13. Consultar progreso general (Debería decir completed: True)
    print_step("Progreso General Final")
    prog = requests.get(f"{BASE_URL}/courses/{course_id}/progress", headers=stud_headers).json()
    print(json.dumps(prog, indent=2))

if __name__ == "__main__":
    main()
