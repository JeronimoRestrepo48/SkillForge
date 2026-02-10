"""
Expande el contenido de los cursos: descripciones largas, info de exámenes/trabajos/calificaciones,
y muchos más módulos y lecciones por curso.
Uso: python manage.py expandir_contenido_cursos
"""
from django.core.management.base import BaseCommand
from catalog.models import Curso, EstadoCurso, Modulo, Leccion
from catalog.models import TipoLeccion


# Por cada curso: descripción larga, info_evaluacion, y lista de (módulo_titulo, duracion_min, [(leccion_titulo, tipo, duracion_min, contenido)])
CONTENIDO_EXTENDIDO = {
    'SQL y bases de datos': (
        '''Este curso cubre en profundidad el lenguaje SQL y el diseño de bases de datos relacionales. Aprenderás desde los fundamentos de consultas SELECT, filtros y ordenación hasta operaciones avanzadas: JOINs (INNER, LEFT, RIGHT, FULL), subconsultas, agregaciones (GROUP BY, HAVING), funciones de ventana y optimización de consultas. Incluye diseño normalizado, integridad referencial, índices y buenas prácticas para modelar datos en entornos empresariales. El contenido está alineado con estándares de la industria y prepara para roles de analista de datos y desarrollador backend. Incluye ejercicios prácticos con bases reales y proyectos guiados.''',
        '''Evaluación continua: quizzes al final de cada módulo (20% de la nota). Trabajo práctico semanal: diseño de esquemas y consultas (30%). Examen teórico-práctico intermedio (25%) y examen final con casos reales (25%). Calificación mínima para aprobar: 70%. La entrega de trabajos tiene fecha límite; se permite una recuperación por módulo.''',
        [
            ('Módulo 1: Fundamentos de SQL', 120, [
                ('Bienvenida y objetivos del curso', 'TEXTO', 15, 'Presentación del programa, metodología y recursos.'),
                ('Introducción a bases de datos relacionales', 'TEXTO', 25, 'Conceptos de tablas, filas, columnas y claves.'),
                ('Instalación del entorno (MySQL/PostgreSQL)', 'TEXTO', 20, 'Guía paso a paso para tener tu propio servidor SQL.'),
                ('SELECT: consultas básicas', 'TEXTO', 25, 'Sintaxis SELECT, FROM, filtros con WHERE y operadores.'),
                ('Ordenación y límites', 'TEXTO', 15, 'ORDER BY, LIMIT y paginación.'),
                ('Quiz módulo 1', 'QUIZ', 15, 'Preguntas de opción múltiple sobre fundamentos.'),
            ]),
            ('Módulo 2: Filtros y funciones', 150, [
                ('Operadores lógicos y comparación', 'TEXTO', 20, 'AND, OR, NOT, IN, BETWEEN, LIKE.'),
                ('Valores nulos (NULL)', 'TEXTO', 15, 'Manejo de NULL con IS NULL, COALESCE.'),
                ('Funciones escalares', 'TEXTO', 25, 'Funciones de texto, número y fecha.'),
                ('Agregaciones: COUNT, SUM, AVG, MIN, MAX', 'TEXTO', 25, 'Uso de funciones de agregación.'),
                ('GROUP BY y HAVING', 'TEXTO', 30, 'Agrupar resultados y filtrar grupos.'),
                ('Práctica: reportes agregados', 'PRACTICA', 25, 'Ejercicio guiado con datos de ventas.'),
            ]),
            ('Módulo 3: JOINs y relaciones', 180, [
                ('Relaciones entre tablas', 'TEXTO', 20, 'Claves primarias y foráneas.'),
                ('INNER JOIN', 'TEXTO', 25, 'Combinar tablas con coincidencia exacta.'),
                ('LEFT, RIGHT y FULL OUTER JOIN', 'TEXTO', 30, 'Incluir filas sin coincidencia.'),
                ('Self-join y múltiples JOINs', 'TEXTO', 25, 'Consultas sobre la misma tabla y varias tablas.'),
                ('Subconsultas (subqueries)', 'TEXTO', 35, 'SELECT anidados, EXISTS, IN con subconsultas.'),
                ('Práctica: modelo e-commerce', 'PRACTICA', 35, 'Consultas sobre clientes, pedidos y productos.'),
            ]),
            ('Módulo 4: Diseño y optimización', 120, [
                ('Normalización (1FN, 2FN, 3FN)', 'TEXTO', 30, 'Eliminar redundancia y anomalías.'),
                ('Índices y rendimiento', 'TEXTO', 25, 'Cuándo y cómo crear índices.'),
                ('Vistas y stored procedures (conceptos)', 'TEXTO', 25, 'Reutilización de consultas.'),
                ('Buenas prácticas y seguridad', 'TEXTO', 20, 'SQL injection, permisos, backups.'),
                ('Proyecto final: diseño y consultas', 'PRACTICA', 20, 'Entrega de un modelo y conjunto de consultas.'),
            ]),
        ],
    ),
    'Español para negocios': (
        '''Curso especializado en comunicación profesional en español para entornos corporativos y negocios internacionales. Desarrollarás competencias en redacción de correos formales, informes ejecutivos, presentaciones orales y reuniones de trabajo. Incluye vocabulario técnico comercial, convenciones culturales en Latinoamérica y España, y práctica con casos reales: negociación, ventas y atención al cliente. Ideal para profesionales no nativos que trabajan con mercados hispanohablantes o para hispanohablantes que desean pulir su comunicación escrita y oral en contextos empresariales.''',
        '''Sistema de evaluación: participación en foros y ejercicios escritos (20%). Tres trabajos entregables: correo formal, informe breve y guion de presentación (40%). Examen oral simulado (videollamada o grabación) (20%). Examen final escrito de comprensión y redacción (20%). Calificación mínima 70%. Retroalimentación detallada en cada trabajo.''',
        [
            ('Módulo 1: Comunicación escrita formal', 90, [
                ('Bienvenida y objetivos', 'TEXTO', 10, 'Presentación del curso y criterios de evaluación.'),
                ('Estructura del correo profesional', 'TEXTO', 20, 'Saludos, cuerpo, cierre y tono.'),
                ('Fórmulas de cortesía y convenciones', 'TEXTO', 20, 'Usted, fórmulas estándar en español.'),
                ('Redacción de correos: peticiones y respuestas', 'TEXTO', 25, 'Modelos y ejemplos.'),
                ('Práctica: redactar un correo', 'PRACTICA', 15, 'Ejercicio con corrección guiada.'),
            ]),
            ('Módulo 2: Informes y documentación', 100, [
                ('Tipos de informes en el ámbito empresarial', 'TEXTO', 20, 'Informes técnicos, ejecutivos, de avance.'),
                ('Estructura y cohesión', 'TEXTO', 25, 'Introducción, desarrollo, conclusiones.'),
                ('Vocabulario y conectores', 'TEXTO', 20, 'Enlace de ideas y registro formal.'),
                ('Trabajo entregable: informe breve', 'PRACTICA', 25, 'Instrucciones y rúbrica.'),
            ]),
            ('Módulo 3: Presentaciones orales', 110, [
                ('Cómo estructurar una presentación', 'TEXTO', 25, 'Apertura, mensaje clave, cierre.'),
                ('Lenguaje corporal y voz', 'TEXTO', 20, 'Consejos para hablar en público.'),
                ('Responder preguntas y objeciones', 'TEXTO', 20, 'Estrategias en reuniones.'),
                ('Grabación: presentación de 5 minutos', 'PRACTICA', 35, 'Entrega en video.'),
            ]),
            ('Módulo 4: Negociación y cultura', 90, [
                ('Vocabulario de negocios y finanzas', 'TEXTO', 25, 'Términos clave en español.'),
                ('Diferencias culturales (LATAM vs España)', 'TEXTO', 25, 'Formalidad, horarios, regalos.'),
                ('Simulación de reunión', 'PRACTICA', 30, 'Role-play guiado.'),
            ]),
        ],
    ),
    'Introducción a Python': (
        '''Curso completo para aprender Python desde cero. Cubre sintaxis, tipos de datos, estructuras de control, funciones, módulos, manejo de archivos y una introducción a la programación orientada a objetos. Incluye ejercicios prácticos en cada tema y un proyecto final. El contenido está diseñado para que al final puedas leer y escribir scripts útiles y sentar las bases para frameworks como Django o análisis de datos.''',
        '''Evaluación: quizzes por módulo (25%), ejercicios de código semanales (35%), proyecto intermedio (20%) y examen final teórico-práctico (20%). Nota mínima 70%. Los trabajos de código se evalúan con rúbrica de corrección automática y revisión de buenas prácticas.''',
        [
            ('Módulo 1: Primeros pasos', 90, [
                ('Instalación y primer programa', 'TEXTO', 20, 'Python en Windows/Mac/Linux, IDLE y editores.'),
                ('Variables y tipos de datos', 'TEXTO', 25, 'int, float, str, bool.'),
                ('Entrada y salida', 'TEXTO', 15, 'print, input, formato de cadenas.'),
                ('Operadores', 'TEXTO', 20, 'Aritméticos, comparación, lógicos.'),
                ('Quiz módulo 1', 'QUIZ', 10, 'Preguntas de opción múltiple.'),
            ]),
            ('Módulo 2: Control de flujo', 120, [
                ('Condicionales: if, elif, else', 'TEXTO', 25, 'Estructuras condicionales.'),
                ('Bucles: for y while', 'TEXTO', 30, 'Iteraciones y bucles anidados.'),
                ('Listas y tuplas', 'TEXTO', 35, 'Creación, índices, métodos.'),
                ('Práctica: listas y bucles', 'PRACTICA', 20, 'Ejercicios guiados.'),
            ]),
            ('Módulo 3: Funciones y módulos', 100, [
                ('Definición de funciones', 'TEXTO', 30, 'Parámetros, return, alcance.'),
                ('Módulos y import', 'TEXTO', 25, 'Organizar código en archivos.'),
                ('Manejo de archivos', 'TEXTO', 25, 'Abrir, leer y escribir archivos.'),
                ('Proyecto: procesar un archivo', 'PRACTICA', 15, 'Entrega de script.'),
            ]),
            ('Módulo 4: POO básica', 80, [
                ('Clases y objetos', 'TEXTO', 25, 'Atributos y métodos.'),
                ('Constructores y herencia', 'TEXTO', 30, '__init__, super().'),
                ('Proyecto final', 'PRACTICA', 20, 'Programa que integre lo aprendido.'),
            ]),
        ],
    ),
    'Django: Backend profesional': (
        '''Formación en Django para desarrollar aplicaciones web robustas: modelos ORM, vistas, plantillas, formularios, autenticación y APIs REST. Incluye buenas prácticas de seguridad, testing y despliegue. El curso asume conocimientos básicos de Python.''',
        '''Quizzes por módulo (20%), prácticas de código (30%), proyecto API REST (30%) y examen final (20%). Nota mínima 70%.''',
        [
            ('Módulo 1: Proyecto y modelos', 120, [
                ('Crear proyecto y apps', 'TEXTO', 20, 'django-admin, estructura.'),
                ('Modelos y migraciones', 'TEXTO', 35, 'Campos, relaciones, Meta.'),
                ('Admin site', 'TEXTO', 25, 'Registro y personalización.'),
                ('Práctica: modelo Blog', 'PRACTICA', 30, 'Ejercicio guiado.'),
            ]),
            ('Módulo 2: Vistas y plantillas', 130, [
                ('Vistas basadas en funciones y clases', 'TEXTO', 30, 'FBV, CBV, get_object_or_404.'),
                ('Plantillas y herencia', 'TEXTO', 30, 'DTL, filtros, includes.'),
                ('Formularios', 'TEXTO', 35, 'ModelForm, validación.'),
                ('Práctica: CRUD completo', 'PRACTICA', 25, 'Crear, leer, actualizar, borrar.'),
            ]),
            ('Módulo 3: Auth y APIs', 140, [
                ('Autenticación y permisos', 'TEXTO', 35, 'User, login, decorators.'),
                ('DRF: serializers y ViewSets', 'TEXTO', 40, 'REST framework.'),
                ('Proyecto: API REST', 'PRACTICA', 45, 'Entrega de API documentada.'),
            ]),
        ],
    ),
    'JavaScript moderno': (
        '''ES6+, asincronía (promesas, async/await), manipulación del DOM, módulos y herramientas modernas. Incluye ejercicios en navegador y Node.js.''',
        '''Quizzes (20%), ejercicios de código (40%), proyecto frontend (40%). Nota mínima 70%.''',
        [
            ('Módulo 1: Fundamentos modernos', 100, [
                ('Variables: let, const', 'TEXTO', 15, 'Alcance y buenas prácticas.'),
                ('Funciones flecha y parámetros', 'TEXTO', 20, 'Arrow functions, rest, spread.'),
                ('Template literals y destructuring', 'TEXTO', 20, 'Strings y asignación.'),
                ('Módulos ES6', 'TEXTO', 20, 'import/export.'),
                ('Quiz', 'QUIZ', 15, 'Preguntas.'),
            ]),
            ('Módulo 2: Asincronía y DOM', 120, [
                ('Promesas y async/await', 'TEXTO', 35, 'fetch, manejo de errores.'),
                ('DOM y eventos', 'TEXTO', 35, 'querySelector, addEventListener.'),
                ('Práctica: app con API', 'PRACTICA', 40, 'Consumir API y mostrar datos.'),
            ]),
        ],
    ),
    'React desde cero': (
        '''Componentes, estado, hooks (useState, useEffect), contexto y enrutamiento. Proyecto guiado de una SPA.''',
        '''Quizzes (20%), prácticas (40%), proyecto SPA (40%). Nota mínima 70%.''',
        [
            ('Módulo 1: Componentes y JSX', 90, [
                ('Crear proyecto (Vite/CRA)', 'TEXTO', 15, 'Setup.'),
                ('Componentes funcionales y props', 'TEXTO', 25, 'Composición.'),
                ('Estado con useState', 'TEXTO', 25, 'Hooks.'),
                ('Práctica: lista interactiva', 'PRACTICA', 20, 'Ejercicio.'),
            ]),
            ('Módulo 2: Hooks y rutas', 100, [
                ('useEffect y ciclo de vida', 'TEXTO', 25, 'Efectos secundarios.'),
                ('React Router', 'TEXTO', 30, 'Navegación.'),
                ('Proyecto final', 'PRACTICA', 35, 'SPA con varias vistas.'),
            ]),
        ],
    ),
    'Git y control de versiones': (
        '''Ramas, merge, rebase, flujo de trabajo en equipo, GitHub/GitLab. Comandos esenciales y resolución de conflictos.''',
        '''Quizzes (30%), ejercicios con repositorio (70%). Nota mínima 70%.''',
        [
            ('Módulo 1: Fundamentos', 60, [
                ('Instalación y configuración', 'TEXTO', 10, 'git config.'),
                ('Commit, log, diff', 'TEXTO', 20, 'Flujo básico.'),
                ('Ramas y merge', 'TEXTO', 25, 'branch, checkout, merge.'),
            ]),
            ('Módulo 2: Colaboración', 60, [
                ('Remotes y push/pull', 'TEXTO', 20, 'origin, fetch.'),
                ('Conflictos y buenas prácticas', 'TEXTO', 25, 'Resolución.'),
                ('Práctica: flujo completo', 'PRACTICA', 15, 'Simulación en equipo.'),
            ]),
        ],
    ),
    'Diseño UI/UX con Figma': (
        '''Prototipos, sistemas de diseño, componentes y colaboración. Incluye diseño de una app móvil y preparación para desarrolladores.''',
        '''Entregas de diseños por módulo (60%), proyecto final (40%). Nota mínima 70%.''',
        [
            ('Módulo 1: Interfaz de Figma', 70, [
                ('Herramientas y atajos', 'TEXTO', 25, 'Selección, formas, texto.'),
                ('Frames y auto layout', 'TEXTO', 25, 'Estructura.'),
                ('Práctica: pantalla simple', 'PRACTICA', 15, 'Diseño guiado.'),
            ]),
            ('Módulo 2: Componentes y prototipos', 80, [
                ('Componentes y variantes', 'TEXTO', 30, 'Reutilización.'),
                ('Prototipos y navegación', 'TEXTO', 25, 'Links entre frames.'),
                ('Proyecto: 5 pantallas', 'PRACTICA', 20, 'Entrega.'),
            ]),
        ],
    ),
    'Inglés nivel A1-A2': (
        '''Gramática y vocabulario básico: presente simple, pasado simple, verbos modales, vocabulario cotidiano y comprensión de textos cortos. Enfocado en comunicación básica.''',
        '''Quizzes por unidad (25%), tareas escritas (35%), examen oral (20%), examen final (20%). Nota mínima 70%.''',
        [
            ('Módulo 1: Presente y vocabulario', 100, [
                ('Present simple', 'TEXTO', 25, 'Afirmativa, negativa, preguntas.'),
                ('Vocabulario: familia y rutinas', 'TEXTO', 25, 'Palabras y frases.'),
                ('Listening y reading', 'TEXTO', 25, 'Ejercicios.'),
                ('Quiz', 'QUIZ', 15, 'Preguntas.'),
            ]),
            ('Módulo 2: Pasado y futuro', 100, [
                ('Past simple', 'TEXTO', 25, 'Verbos regulares e irregulares.'),
                ('Going to y will', 'TEXTO', 25, 'Futuro.'),
                ('Práctica integrada', 'PRACTICA', 35, 'Ejercicios combinados.'),
            ]),
        ],
    ),
    'Finanzas personales': (
        '''Ahorro, presupuesto, deudas y conceptos básicos de inversión. Herramientas prácticas para tomar decisiones financieras.''',
        '''Cuestionarios (30%), trabajo de presupuesto (40%), examen final (30%). Nota mínima 70%.''',
        [
            ('Módulo 1: Presupuesto', 60, [
                ('Ingresos y gastos', 'TEXTO', 20, 'Categorías.'),
                ('Herramientas de control', 'TEXTO', 20, 'Plantillas.'),
                ('Trabajo: mi presupuesto', 'PRACTICA', 15, 'Entrega.'),
            ]),
            ('Módulo 2: Ahorro e inversión', 60, [
                ('Fondo de emergencia', 'TEXTO', 20, 'Conceptos.'),
                ('Introducción a inversión', 'TEXTO', 25, 'Riesgo y diversificación.'),
                ('Quiz final', 'QUIZ', 10, 'Preguntas.'),
            ]),
        ],
    ),
}


def apply_contenido(curso):
    """Aplica descripción larga, info_evaluacion y módulos/lecciones si está en CONTENIDO_EXTENDIDO."""
    data = CONTENIDO_EXTENDIDO.get(curso.titulo)
    if not data:
        return False
    descripcion, info_evaluacion, modulos_data = data
    curso.descripcion = descripcion
    curso.info_evaluacion = info_evaluacion
    curso.save(update_fields=['descripcion', 'info_evaluacion'])

    # Si ya tiene muchos módulos, no sobrescribir
    if curso.modulos.count() >= 3:
        return True

    # Crear módulos y lecciones (eliminar los existentes si son solo el genérico)
    existing = list(curso.modulos.all().order_by('orden'))
    if len(existing) == 1 and existing[0].lecciones.count() <= 2:
        existing[0].lecciones.all().delete()
        existing[0].delete()

    orden_m = 0
    for titulo_mod, duracion_min, lecciones_list in modulos_data:
        mod = Modulo.objects.create(
            curso=curso,
            titulo=titulo_mod,
            orden=orden_m,
            duracion_minutos=duracion_min,
        )
        for orden_l, (titulo_lec, tipo, dur, contenido) in enumerate(lecciones_list):
            Leccion.objects.create(
                modulo=mod,
                titulo=titulo_lec,
                tipo=tipo,
                contenido=contenido,
                orden=orden_l,
                duracion_minutos=dur,
            )
        orden_m += 1
    return True


class Command(BaseCommand):
    help = 'Expande descripciones, info de evaluación y contenido (módulos/lecciones) de los cursos'

    def handle(self, *args, **options):
        cursos = Curso.objects.filter(estado=EstadoCurso.PUBLICADO)
        updated = 0
        for curso in cursos:
            if apply_contenido(curso):
                updated += 1
                self.stdout.write(self.style.SUCCESS(f'  Expandido: {curso.titulo}'))
        self.stdout.write(self.style.SUCCESS(f'Contenido expandido en {updated} curso(s).'))
