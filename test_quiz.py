import requests
import json

base_url = "http://localhost/api"

print("1. Getting token...")
resp = requests.post(f"{base_url}/auth/token", json={"username":"instructor", "password":"instructor123"})
if resp.status_code != 200:
    print("Failed to login", resp.text)
    exit(1)
token = resp.json()["access"]
headers = {"Authorization": f"Bearer {token}"}
print("Token obtained.")

print("\n2. Creating Quiz...")
quiz_payload = {
    "titulo": "Prueba Final del Sistema",
    "puntaje_minimo_aprobacion": 60.0,
    "lesson_id": 4, # Seeder lesson "Quiz Final" has id 4
    "questions": [
        {
            "tipo": "OPCION_MULTIPLE",
            "enunciado": "¿Qué es FastAPI?",
            "puntaje": 50.0,
            "sort_order": 1,
            "options": [
                {"texto": "Un framework de Python", "es_correcta": True},
                {"texto": "Una base de datos", "es_correcta": False}
            ]
        },
        {
            "tipo": "ABIERTA",
            "enunciado": "Explica brevemente qué es el glassmorphism.",
            "puntaje": 50.0,
            "sort_order": 2,
            "respuesta_esperada": "Es un estilo de diseño UI que usa fondos translúcidos y desenfocados para crear un efecto de vidrio."
        }
    ]
}

resp = requests.post(f"{base_url}/catalog/lessons/4/quiz", json=quiz_payload, headers=headers)
if resp.status_code != 200:
    print("Failed to create quiz:", resp.text)
    exit(1)
quiz = resp.json()
print("Quiz created. ID:", quiz["id"])
q1_id = next(q["id"] for q in quiz["questions"] if q["tipo"] == "OPCION_MULTIPLE")
q2_id = next(q["id"] for q in quiz["questions"] if q["tipo"] == "ABIERTA")
opt_correct_id = next(opt["id"] for q in quiz["questions"] if q["tipo"] == "OPCION_MULTIPLE" for opt in q["options"] if opt["es_correcta"])

print("\n3. Submitting CORRECT Attempt...")
attempt_payload = {
    "respuestas": [
        {"question_id": q1_id, "selected_option_id": opt_correct_id},
        {"question_id": q2_id, "respuesta_texto": "Es un diseño de interfaz que simula vidrio esmerilado con desenfoque y transparencia."}
    ]
}
resp = requests.post(f"{base_url}/catalog/quizzes/{quiz['id']}/attempts", json=attempt_payload, headers=headers)
print("Correct Attempt Result:")
print(json.dumps(resp.json(), indent=2))

print("\n4. Submitting INCORRECT Attempt...")
attempt_payload2 = {
    "respuestas": [
        {"question_id": q1_id, "selected_option_id": opt_correct_id},
        {"question_id": q2_id, "respuesta_texto": "Los perros son los mejores amigos del hombre."}
    ]
}
resp = requests.post(f"{base_url}/catalog/quizzes/{quiz['id']}/attempts", json=attempt_payload2, headers=headers)
print("Incorrect Attempt Result:")
print(json.dumps(resp.json(), indent=2))
