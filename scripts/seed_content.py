import requests
import json
import time
import subprocess
import os

AUTH_URL = "http://localhost/api/auth"
CATALOG_URL = "http://localhost/api/catalog"

def change_role_to_instructor(username):
    cmd = f'docker exec skillforge2-auth-db-1 psql -U auth -d authdb -c "UPDATE users SET role=\'INSTRUCTOR\' WHERE username=\'{username}\';"'
    subprocess.run(cmd, shell=True, check=True)

def register_user(username, password, email):
    resp = requests.post(f"{AUTH_URL}/register", json={"username": username, "password": password, "email": email})
    return resp

def login(username, password):
    resp = requests.post(f"{AUTH_URL}/token", json={"username": username, "password": password})
    return resp.json()["access"]

def create_instructor_profile(token, user_id, profile_data):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.put(f"{AUTH_URL}/instructors/{user_id}/profile", json=profile_data, headers=headers)
    return resp.json()

def create_category(name):
    cmd = f'docker exec skillforge2-catalog-db-1 psql -U catalog -d catalogdb -c "INSERT INTO categories (name) SELECT \'{name}\' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name=\'{name}\');"'
    subprocess.run(cmd, shell=True, check=True)
    
    cats = requests.get(f"{CATALOG_URL}/categories").json()
    for c in cats.get("results", []):
        if c["name"] == name:
            return c
    return None

def create_course(token, course_data):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{CATALOG_URL}/courses/", json=course_data, headers=headers)
    if resp.status_code >= 400:
        print("Error creating course:", resp.text)
    return resp.json()

def create_module(token, course_id, module_data):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{CATALOG_URL}/courses/{course_id}/modules", json=module_data, headers=headers)
    return resp.json()

def create_lesson(token, module_id, lesson_data):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{CATALOG_URL}/modules/{module_id}/lessons", json=lesson_data, headers=headers)
    return resp.json()

def create_quiz(token, lesson_id, quiz_data):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{CATALOG_URL}/lessons/{lesson_id}/quiz", json=quiz_data, headers=headers)
    return resp.json()

def create_trayectoria(token, trayectoria_data):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{CATALOG_URL}/trayectorias/", json=trayectoria_data, headers=headers)
    return resp.json()

def add_curso_to_trayectoria(token, trayectoria_id, course_id, sort_order):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{CATALOG_URL}/trayectorias/{trayectoria_id}/cursos", json={"course_id": course_id, "sort_order": sort_order}, headers=headers)
    return resp.json()

def add_rating(token, course_id, score, comment):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{CATALOG_URL}/courses/{course_id}/ratings", json={"score": score, "comment": comment}, headers=headers)
    return resp.json()

def main():
    print("=== EMPEZANDO SEED ===")

    # 1. Instructores
    instructors_data = [
        {
            "user": {"username": "jane_ux", "password": "password123", "email": "jane@example.com"},
            "profile": {
                "bio": "Diseñadora UX/UI con más de 8 años de experiencia en startups de Silicon Valley. Me especializo en crear experiencias centradas en el usuario y accesibles. Mi pasión es enseñar cómo el buen diseño mejora la vida de las personas.",
                "carrera": "Diseñadora UX/UI Senior",
                "estudios": "Maestría en Interacción Humano-Computadora, Universidad de Stanford.",
                "linkedin_url": "https://linkedin.com/in/jane-ux",
                "avatar_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop"
            }
        },
        {
            "user": {"username": "john_back", "password": "password123", "email": "john@example.com"},
            "profile": {
                "bio": "Ingeniero de Software especializado en Backend y Microservicios con 10 años de experiencia. He escalado sistemas para millones de usuarios. Me encanta compartir conocimientos sobre patrones de diseño y arquitecturas limpias.",
                "carrera": "Arquitecto de Software",
                "estudios": "Ingeniería de Sistemas, MIT. Certificación AWS Solutions Architect.",
                "linkedin_url": "https://linkedin.com/in/john-backend",
                "avatar_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&h=400&fit=crop"
            }
        },
        {
            "user": {"username": "maria_data", "password": "password123", "email": "maria@example.com"},
            "profile": {
                "bio": "Data Scientist entusiasta por el Machine Learning y la IA generativa. Trabajé en grandes corporaciones optimizando modelos de predicción. Mi objetivo es desmitificar la IA para todos.",
                "carrera": "Lead Data Scientist",
                "estudios": "Doctorado en Ciencias de la Computación, Universidad Nacional.",
                "linkedin_url": "https://linkedin.com/in/maria-data",
                "avatar_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=400&fit=crop"
            }
        },
        {
            "user": {"username": "alex_sec", "password": "password123", "email": "alex@example.com"},
            "profile": {
                "bio": "Especialista en Ciberseguridad y Ethical Hacking. Protegiendo infraestructuras críticas desde hace más de una década. Descubridor de múltiples vulnerabilidades CVE.",
                "carrera": "Ethical Hacker",
                "estudios": "Certificaciones CEH, CISSP y OSCP.",
                "linkedin_url": "https://linkedin.com/in/alex-sec",
                "avatar_url": "https://images.unsplash.com/photo-1598550874175-4dad81a4dcc4?w=400&h=400&fit=crop"
            }
        }
    ]

    # Create instructors
    instructor_tokens = {}
    instructor_ids = {}
    for data in instructors_data:
        u = data["user"]
        # Try to register
        register_user(u["username"], u["password"], u["email"])
        change_role_to_instructor(u["username"])
        
        # Login
        token = login(u["username"], u["password"])
        instructor_tokens[u["username"]] = token
        
        # Get user details
        me = requests.get(f"{AUTH_URL}/me", headers={"Authorization": f"Bearer {token}"}).json()
        instructor_ids[u["username"]] = me["id"]
        
        # Create profile
        create_instructor_profile(token, me["id"], data["profile"])
        print(f"Instructor {u['username']} creado y perfil configurado.")

    # Create students for ratings
    student_tokens = []
    for i in range(1, 4):
        username = f"student_seed_{i}"
        register_user(username, "password123", f"student{i}@test.com")
        token = login(username, "password123")
        student_tokens.append(token)

    # 2. Categorias
    cat_names = ["Desarrollo Web", "Data Science", "Arquitectura de Software", "Diseño UX/UI", "Ciberseguridad"]
    categories = {}
    for name in cat_names:
        c = create_category(name)
        if c:
            categories[name] = c["id"]
            print(f"Categoría {name} lista.")

    # 3. Cursos
    courses_data = [
        # Desarrollo Web
        {"title": "React.js Avanzado: Hooks y Context", "cat": "Desarrollo Web", "inst": "jane_ux", "price": 120000, "cert": False, "img": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=500&fit=crop", "desc": "Domina React.js aprendiendo sobre Hooks personalizados, Context API y optimización de rendimiento. Construye aplicaciones web escalables y modernas con las mejores prácticas de la industria."},
        {"title": "Node.js y Express desde Cero", "cat": "Desarrollo Web", "inst": "john_back", "price": 95000, "cert": False, "img": "https://images.unsplash.com/photo-1555099962-4199c345e5dd?w=800&h=500&fit=crop", "desc": "Aprende a crear servidores rápidos y seguros usando Node.js y Express. Comprende el middleware, el enrutamiento y la conexión a bases de datos NoSQL."},
        {"title": "CSS Grid y Flexbox Masterclass", "cat": "Desarrollo Web", "inst": "jane_ux", "price": 60000, "cert": False, "img": "https://images.unsplash.com/photo-1547658719-b28e6f1f15e5?w=800&h=500&fit=crop", "desc": "Crea layouts responsivos y modernos sin depender de frameworks. Entiende a fondo cómo utilizar CSS Grid y Flexbox para maquetar cualquier diseño."},
        {"title": "Certificación Fullstack MERN", "cat": "Desarrollo Web", "inst": "john_back", "price": 250000, "cert": True, "img": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&h=500&fit=crop", "desc": "Curso completo con certificación en MongoDB, Express, React y Node.js. Incluye exámenes modulares y un examen final para avalar tus conocimientos."},
        
        # Data Science
        {"title": "Python para Análisis de Datos", "cat": "Data Science", "inst": "maria_data", "price": 85000, "cert": False, "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=500&fit=crop", "desc": "Aprende Pandas, NumPy y Matplotlib para manipular y visualizar grandes volúmenes de datos. Empieza tu camino en Data Science con fundamentos sólidos."},
        {"title": "Certificación en Machine Learning con Scikit-Learn", "cat": "Data Science", "inst": "maria_data", "price": 280000, "cert": True, "img": "https://images.unsplash.com/photo-1504868584819-eb814187f54c?w=800&h=500&fit=crop", "desc": "Domina algoritmos de clasificación, regresión y clustering. Curso avalado con exámenes rigurosos para validar tus competencias en Machine Learning."},
        {"title": "Deep Learning con TensorFlow", "cat": "Data Science", "inst": "maria_data", "price": 150000, "cert": False, "img": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&h=500&fit=crop", "desc": "Introducción a redes neuronales profundas. Aprende a crear modelos predictivos avanzados utilizando TensorFlow y Keras."},
        
        # Arquitectura
        {"title": "Diseño de Microservicios", "cat": "Arquitectura de Software", "inst": "john_back", "price": 180000, "cert": False, "img": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=500&fit=crop", "desc": "Rompe el monolito. Aprende a diseñar, comunicar y desplegar microservicios escalables utilizando contenedores y orquestadores."},
        {"title": "Patrones de Arquitectura Cloud", "cat": "Arquitectura de Software", "inst": "john_back", "price": 195000, "cert": False, "img": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=500&fit=crop", "desc": "Descubre los patrones esenciales para desplegar aplicaciones resilientes en la nube. Tolerancia a fallos, balanceo de carga y auto-escalado."},
        {"title": "Certificación AWS Serverless", "cat": "Arquitectura de Software", "inst": "john_back", "price": 300000, "cert": True, "img": "https://images.unsplash.com/photo-1614064641913-6b70fea5af2e?w=800&h=500&fit=crop", "desc": "Domina AWS Lambda, API Gateway y DynamoDB. Obtén tu certificado tras superar las pruebas prácticas y teóricas de este curso."},
        
        # UX/UI
        {"title": "Fundamentos de Diseño UX", "cat": "Diseño UX/UI", "inst": "jane_ux", "price": 75000, "cert": False, "img": "https://images.unsplash.com/photo-1561070791-2526d3098f71?w=800&h=500&fit=crop", "desc": "Aprende a investigar a los usuarios y crear arquitecturas de información sólidas. El primer paso para convertirte en un experto UX."},
        {"title": "Prototipado Avanzado en Figma", "cat": "Diseño UX/UI", "inst": "jane_ux", "price": 90000, "cert": False, "img": "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?w=800&h=500&fit=crop", "desc": "Crea prototipos interactivos y animaciones fluidas directamente en Figma. Sorprende a tus clientes con presentaciones realistas."},
        
        # Ciberseguridad
        {"title": "Introducción al Ethical Hacking", "cat": "Ciberseguridad", "inst": "alex_sec", "price": 110000, "cert": False, "img": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&h=500&fit=crop", "desc": "Conoce cómo piensan los atacantes para poder defenderte. Técnicas de reconocimiento y explotación básica explicadas de forma segura."},
        {"title": "Certificación en Seguridad Web (OWASP)", "cat": "Ciberseguridad", "inst": "alex_sec", "price": 270000, "cert": True, "img": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&h=500&fit=crop", "desc": "Domina el OWASP Top 10. Evalúa tus conocimientos con laboratorios interactivos y exámenes para certificarte como experto en seguridad web."},
        {"title": "Análisis Forense Digital", "cat": "Ciberseguridad", "inst": "alex_sec", "price": 130000, "cert": False, "img": "https://images.unsplash.com/photo-1563206767-5b38d0010d2c?w=800&h=500&fit=crop", "desc": "Aprende a recuperar evidencia digital después de un incidente. Análisis de memoria, discos duros y tráfico de red."}
    ]

    created_courses = []

    for c in courses_data:
        token = instructor_tokens[c["inst"]]
        payload = {
            "title": c["title"],
            "description": c["desc"],
            "category_id": categories[c["cat"]],
            "price": c["price"],
            "status": "PUBLISHED",
            "nivel_dificultad": "INTERMEDIO",
            "duracion_horas": 15,
            "es_certificacion": c["cert"],
            "imagen_url": c["img"]
        }
        
        course_obj = create_course(token, payload)
        if "id" not in course_obj:
            print("Saltando creación (quizás ya existe o error)")
            continue
            
        course_id = course_obj["id"]
        created_courses.append(course_obj)
        print(f"Curso creado: {c['title']} (ID: {course_id})")

        # Create modules and lessons
        if c["cert"]:
            # Module 1: Normal
            m1 = create_module(token, course_id, {"title": "Módulo 1: Fundamentos", "sort_order": 1})
            create_lesson(token, m1["id"], {"title": "Conceptos Clave", "content_type": "TEXTO", "content": "Bienvenido al curso. Aquí veremos los fundamentos teóricos.", "sort_order": 1, "duration_minutes": 20})
            
            # Module 2: Examen Módulo
            m2 = create_module(token, course_id, {"title": "Módulo 2: Evaluación Intermedia", "sort_order": 2, "es_examen_modulo": True})
            l2 = create_lesson(token, m2["id"], {"title": "Quiz Módulo 2", "content_type": "QUIZ", "sort_order": 1, "duration_minutes": 15})
            create_quiz(token, l2["id"], {
                "passing_score": 50.0,
                "questions": [
                    {"question_text": "¿Cuál es la función principal de este concepto?", "question_type": "MULTIPLE_CHOICE", "points": 50.0, "options": [{"option_text": "Respuesta correcta", "is_correct": True}, {"option_text": "Respuesta incorrecta", "is_correct": False}]},
                    {"question_text": "Mencione una ventaja de usar esto.", "question_type": "OPEN", "points": 50.0, "expected_answer": "Es rápido y seguro."}
                ]
            })

            # Module 3: Examen Final
            m3 = create_module(token, course_id, {"title": "Módulo 3: Examen Final", "sort_order": 3, "es_examen_final": True})
            l3 = create_lesson(token, m3["id"], {"title": "Examen Final de Certificación", "content_type": "QUIZ", "sort_order": 1, "duration_minutes": 45})
            create_quiz(token, l3["id"], {
                "passing_score": 50.0,
                "questions": [
                    {"question_text": "¿Qué arquitectura se recomienda aquí?", "question_type": "MULTIPLE_CHOICE", "points": 50.0, "options": [{"option_text": "Microservicios", "is_correct": True}, {"option_text": "Monolítica", "is_correct": False}]},
                    {"question_text": "Describe el caso de uso principal.", "question_type": "OPEN", "points": 50.0, "expected_answer": "Sistemas de alta concurrencia."}
                ]
            })
        else:
            # Normal course
            for i in range(1, 3):
                m = create_module(token, course_id, {"title": f"Módulo {i}", "sort_order": i})
                create_lesson(token, m["id"], {"title": f"Lección de Lectura {i}", "content_type": "TEXTO", "content": "Contenido de texto importante para esta lección.", "sort_order": 1, "duration_minutes": 10})
                create_lesson(token, m["id"], {"title": f"Lección de Video {i}", "content_type": "VIDEO", "content": "https://www.w3schools.com/html/mov_bbb.mp4", "sort_order": 2, "duration_minutes": 25})

        # Add ratings using students
        for i, s_token in enumerate(student_tokens):
            scores = [5, 4, 5, 3, 4]
            comments = ["Excelente curso, muy recomendado.", "Buen contenido, claro y conciso.", "Me encantó la didáctica del instructor.", "Un poco básico, pero bien explicado.", "Cumplió mis expectativas totalmente."]
            score = scores[(course_id + i) % len(scores)]
            comment = comments[(course_id + i) % len(comments)]
            add_rating(s_token, course_id, score, comment)

    # 4. Trayectorias
    trayectorias_data = [
        {"nombre": "Ruta de Arquitectura y Backend", "desc": "Conviértete en un arquitecto de software sólido aprendiendo Node, Arquitectura Cloud y Microservicios.", "img": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=500&fit=crop", "cat": "Arquitectura de Software"},
        {"nombre": "Ruta de Diseño y Frontend", "desc": "De los wireframes al código interactivo. Aprende UX/UI y frameworks frontend como React.", "img": "https://images.unsplash.com/photo-1507608158173-1dcec673a2e5?w=800&h=500&fit=crop", "cat": "Desarrollo Web"}
    ]

    t_objects = []
    # Usar admin para trayectorias
    register_user("admin_seed", "password123", "adminseed@test.com")
    cmd = f'docker exec skillforge2-auth-db-1 psql -U auth -d authdb -c "UPDATE users SET role=\'admin\' WHERE username=\'admin_seed\';"'
    subprocess.run(cmd, shell=True, check=True)
    admin_token = login("admin_seed", "password123")

    for t in trayectorias_data:
        resp = create_trayectoria(admin_token, {
            "nombre": t["nombre"],
            "descripcion": t["desc"],
            "categoria_general": t["cat"],
            "imagen_url": t["img"]
        })
        if "id" in resp:
            t_objects.append(resp)
            print(f"Trayectoria creada: {t['nombre']}")
        else:
            print("Error tray:", resp)

    # Agregar cursos a la trayectoria 1
    t1_courses = [c for c in created_courses if c["category_id"] in [categories.get("Arquitectura de Software"), categories.get("Desarrollo Web")]]
    for idx, c in enumerate(t1_courses[:4]): # Max 4
        if len(t_objects) > 0:
            add_curso_to_trayectoria(admin_token, t_objects[0]["id"], c["id"], idx+1)

    # Agregar cursos a la trayectoria 2
    t2_courses = [c for c in created_courses if c["category_id"] in [categories.get("Diseño UX/UI"), categories.get("Desarrollo Web")]]
    for idx, c in enumerate(t2_courses[:4]):
        if len(t_objects) > 1:
            add_curso_to_trayectoria(admin_token, t_objects[1]["id"], c["id"], idx+1)

    print("=== SEED COMPLETADO ===")

if __name__ == "__main__":
    main()
