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
    'Illustrator para diseñadores': (
        '''Curso profesional de Adobe Illustrator enfocado en vectorización e ilustración digital para diseñadores gráficos. Aprenderás desde los fundamentos del espacio de trabajo y herramientas de dibujo vectorial hasta técnicas avanzadas: trazos, rellenos, malla de degradado, pinceles personalizados, símbolos y máscaras de recorte. Incluye creación de logotipos, iconografía, patrones, ilustraciones editoriales y preparación de archivos para impresión y web. El contenido cubre flujos de trabajo con tipografía, color (Pantone, CMYK, RGB) y exportación multiformato. Cada módulo incluye ejercicios prácticos y un proyecto final de identidad visual.''',
        '''Evaluación: entregas de ejercicios por módulo (30%), proyecto intermedio de logotipo e iconografía (30%), proyecto final de identidad visual completa (30%), participación en foros y críticas de diseño (10%). Calificación mínima para aprobar: 70%. Los trabajos se evalúan con rúbrica de originalidad, limpieza vectorial, uso del color y coherencia con el brief.''',
        [
            ('Módulo 1: Espacio de trabajo y herramientas básicas', 100, [
                ('Bienvenida e introducción al curso', 'TEXTO', 10, 'Objetivos, metodología y recursos necesarios para el curso.'),
                ('Interfaz de Illustrator y personalización', 'TEXTO', 25, 'Paneles, mesas de trabajo, atajos de teclado y preferencias.'),
                ('Herramientas de selección y formas básicas', 'TEXTO', 25, 'Rectángulo, elipse, polígono, estrella y pathfinder.'),
                ('Pluma y curvas Bézier', 'TEXTO', 25, 'Dibujo con la herramienta pluma, nodos y tiradores.'),
                ('Práctica: composición geométrica', 'PRACTICA', 15, 'Crear una composición con formas y colores planos.'),
            ]),
            ('Módulo 2: Color, trazos y rellenos', 110, [
                ('Modelos de color: RGB, CMYK y Pantone', 'TEXTO', 25, 'Cuándo usar cada modelo y gestión del color.'),
                ('Degradados lineales, radiales y malla de degradado', 'TEXTO', 25, 'Transiciones de color complejas y realistas.'),
                ('Trazos avanzados y perfiles de ancho', 'TEXTO', 20, 'Personalización de trazos, puntas de flecha y pinceles.'),
                ('Patrones y motivos', 'TEXTO', 20, 'Creación de patrones repetitivos (seamless patterns).'),
                ('Práctica: paleta cromática y patrón', 'PRACTICA', 20, 'Diseñar una paleta corporativa y un patrón.'),
            ]),
            ('Módulo 3: Tipografía e iconografía', 120, [
                ('Tipografía en Illustrator', 'TEXTO', 30, 'Textos artísticos, de área, envolventes y estilos de carácter.'),
                ('Diseño de logotipos', 'TEXTO', 30, 'Proceso creativo, bocetado y vectorización de un logo.'),
                ('Creación de iconos SVG', 'TEXTO', 25, 'Iconos consistentes, grilla y exportación SVG.'),
                ('Símbolos y bibliotecas', 'TEXTO', 15, 'Reutilización de elementos y bibliotecas compartidas.'),
                ('Proyecto: logotipo e iconos', 'PRACTICA', 20, 'Entrega de logotipo con variantes y set de iconos.'),
            ]),
            ('Módulo 4: Ilustración y proyecto final', 130, [
                ('Ilustración editorial', 'TEXTO', 30, 'Técnicas de ilustración vectorial: capas, sombras y texturas.'),
                ('Máscaras de recorte y opacidad', 'TEXTO', 25, 'Composiciones con transparencia y clipping masks.'),
                ('Preparación para impresión y web', 'TEXTO', 25, 'Sangrado, marcas de corte, resolución y formatos.'),
                ('Proyecto final: identidad visual', 'PRACTICA', 40, 'Diseño completo de identidad visual para una marca ficticia.'),
                ('Quiz de cierre', 'QUIZ', 10, 'Evaluación de conceptos del módulo.'),
            ]),
        ],
    ),
    'Photoshop esencial': (
        '''Curso completo de Adobe Photoshop orientado a edición fotográfica, composición y retoque profesional. Cubre el espacio de trabajo, capas, máscaras, ajustes de color, selecciones avanzadas, herramientas de retoque, texto, filtros y preparación de archivos. Incluye flujos de trabajo no destructivos con capas de ajuste y objetos inteligentes. Aprenderás a retocar retratos, componer imágenes, crear mockups y optimizar imágenes para web y redes sociales. Cada módulo incluye ejercicios prácticos guiados y un proyecto final de composición fotográfica.''',
        '''Evaluación: entregas prácticas por módulo (30%), proyecto intermedio de retoque fotográfico (25%), proyecto final de composición (35%), quiz por módulo (10%). Calificación mínima 70%. Los trabajos se evalúan por técnica, acabado, uso correcto de herramientas y creatividad.''',
        [
            ('Módulo 1: Interfaz, capas y selecciones', 100, [
                ('Bienvenida y configuración del espacio', 'TEXTO', 10, 'Interfaz de Photoshop, paneles y personalización.'),
                ('Capas: organización y modos de fusión', 'TEXTO', 25, 'Capas normales, grupos, bloqueo y modos de fusión.'),
                ('Selecciones básicas y avanzadas', 'TEXTO', 25, 'Marco, lazo, varita mágica, selección rápida y gama de colores.'),
                ('Máscaras de capa', 'TEXTO', 25, 'Edición no destructiva con máscaras en blanco y negro.'),
                ('Práctica: fotomontaje con selección y máscara', 'PRACTICA', 15, 'Combinar dos fotografías con selección y máscara de capa.'),
            ]),
            ('Módulo 2: Ajustes de color y retoque', 120, [
                ('Capas de ajuste: niveles, curvas, tono/saturación', 'TEXTO', 30, 'Corrección de exposición, contraste y color sin destruir.'),
                ('Herramientas de retoque: tampón, parche, pincel corrector', 'TEXTO', 30, 'Eliminar imperfecciones, clonar y corregir.'),
                ('Retoque de retrato profesional', 'TEXTO', 25, 'Suavizado de piel, ojos, dientes y cabello.'),
                ('Objetos inteligentes y filtros', 'TEXTO', 20, 'Flujo no destructivo con filtros inteligentes.'),
                ('Práctica: retoque de retrato', 'PRACTICA', 15, 'Entrega de retrato retocado con técnica profesional.'),
            ]),
            ('Módulo 3: Texto, formas y efectos', 100, [
                ('Herramienta de texto y estilos', 'TEXTO', 25, 'Texto de punto, de párrafo, deformado y estilos.'),
                ('Formas vectoriales en Photoshop', 'TEXTO', 20, 'Rectángulos, elipses, líneas y formas personalizadas.'),
                ('Estilos de capa: sombra, bisel, resplandor', 'TEXTO', 25, 'Efectos de capa combinados para botones y banners.'),
                ('Acciones y automatización', 'TEXTO', 15, 'Crear acciones para procesos repetitivos.'),
                ('Práctica: banner promocional', 'PRACTICA', 15, 'Diseño de banner para redes sociales.'),
            ]),
            ('Módulo 4: Composición y proyecto final', 130, [
                ('Composición fotográfica avanzada', 'TEXTO', 30, 'Iluminación, perspectiva y coherencia visual.'),
                ('Mockups: presentación de diseños', 'TEXTO', 25, 'Insertar diseños en objetos inteligentes (camisetas, pantallas).'),
                ('Exportación para web, impresión y redes', 'TEXTO', 25, 'Formatos, resolución, perfiles de color y optimización.'),
                ('Proyecto final: composición fotográfica', 'PRACTICA', 40, 'Entrega de composición con al menos 4 elementos combinados.'),
                ('Quiz de cierre', 'QUIZ', 10, 'Evaluación de conceptos del curso.'),
            ]),
        ],
    ),
    'SEO para principiantes': (
        '''Curso completo de posicionamiento en buscadores (SEO) orientado a quienes desean entender cómo funcionan Google y otros motores de búsqueda. Aprenderás desde los fundamentos del SEO (rastreo, indexación y ranking) hasta técnicas on-page (títulos, meta descripciones, encabezados, contenido optimizado), SEO técnico (velocidad, mobile-first, sitemap, robots.txt), link building y SEO local. Incluye uso de herramientas clave como Google Search Console, Google Analytics, Ahrefs/Semrush y Screaming Frog. Cada módulo incluye ejercicios con un sitio web real o simulado y un proyecto final de auditoría SEO.''',
        '''Evaluación: quizzes por módulo (20%), ejercicios prácticos con herramientas (30%), auditoría SEO intermedia (20%), proyecto final de estrategia SEO completa (30%). Calificación mínima 70%. Los trabajos se evalúan por profundidad del análisis, uso correcto de herramientas y calidad de las recomendaciones.''',
        [
            ('Módulo 1: Fundamentos del SEO', 90, [
                ('Bienvenida y objetivos', 'TEXTO', 10, 'Qué es el SEO, por qué importa y qué aprenderás.'),
                ('Cómo funcionan los buscadores', 'TEXTO', 25, 'Rastreo, indexación y algoritmos de ranking.'),
                ('Keywords: investigación de palabras clave', 'TEXTO', 25, 'Intención de búsqueda, volumen y dificultad.'),
                ('Herramientas: Google Search Console', 'TEXTO', 20, 'Configuración, métricas de rendimiento e indexación.'),
                ('Quiz módulo 1', 'QUIZ', 10, 'Preguntas sobre fundamentos.'),
            ]),
            ('Módulo 2: SEO On-Page', 110, [
                ('Títulos, meta descripciones y URLs amigables', 'TEXTO', 25, 'Optimización de etiquetas HTML para CTR y relevancia.'),
                ('Encabezados (H1-H6) y estructura del contenido', 'TEXTO', 20, 'Jerarquía semántica y legibilidad.'),
                ('Contenido optimizado y E-E-A-T', 'TEXTO', 25, 'Experiencia, autoridad y confianza en el contenido.'),
                ('Imágenes, alt text y multimedia', 'TEXTO', 20, 'Optimización de medios para velocidad y accesibilidad.'),
                ('Práctica: optimizar una página', 'PRACTICA', 20, 'Aplicar técnicas on-page a una página real o de ejemplo.'),
            ]),
            ('Módulo 3: SEO Técnico', 100, [
                ('Velocidad de carga y Core Web Vitals', 'TEXTO', 25, 'LCP, FID, CLS y cómo mejorar cada métrica.'),
                ('Mobile-first y diseño responsivo', 'TEXTO', 20, 'Google mobile-first indexing y adaptabilidad.'),
                ('Sitemap XML, robots.txt y datos estructurados', 'TEXTO', 25, 'Facilitar el rastreo e indexación.'),
                ('Auditoría técnica con Screaming Frog', 'TEXTO', 20, 'Errores 404, redirecciones, contenido duplicado.'),
                ('Práctica: auditoría técnica', 'PRACTICA', 10, 'Detectar y documentar problemas técnicos en un sitio.'),
            ]),
            ('Módulo 4: Link building y proyecto final', 100, [
                ('Autoridad de dominio y backlinks', 'TEXTO', 25, 'Qué son, cómo se miden y por qué importan.'),
                ('Estrategias de link building ético', 'TEXTO', 25, 'Guest posting, contenido enlazable, menciones.'),
                ('SEO local: Google Business Profile', 'TEXTO', 20, 'Optimización para negocios locales.'),
                ('Proyecto final: estrategia SEO', 'PRACTICA', 30, 'Auditoría + plan de acción SEO para un sitio.'),
            ]),
        ],
    ),
    'Marketing en redes sociales': (
        '''Curso integral de marketing en redes sociales que cubre estrategia, creación de contenido, gestión de comunidades y análisis de métricas en Facebook, Instagram, LinkedIn y TikTok. Aprenderás a definir objetivos SMART, crear calendarios editoriales, diseñar contenido visual y copywriting, gestionar pauta publicitaria y medir ROI. Incluye casos de estudio reales, herramientas de programación (Buffer, Hootsuite) y técnicas de community management. El curso prepara para gestionar las redes de una marca o negocio de forma profesional.''',
        '''Evaluación: quizzes por módulo (15%), ejercicios prácticos de contenido y pauta (30%), proyecto intermedio de calendario editorial (25%), proyecto final de estrategia de redes para una marca (30%). Calificación mínima 70%. Se evalúa creatividad, coherencia estratégica y dominio de métricas.''',
        [
            ('Módulo 1: Estrategia de redes sociales', 100, [
                ('Bienvenida y panorama actual', 'TEXTO', 15, 'Estadísticas de uso de redes y tendencias.'),
                ('Objetivos SMART y buyer persona', 'TEXTO', 25, 'Definir metas medibles y audiencia objetivo.'),
                ('Plataformas: Facebook, Instagram, LinkedIn, TikTok', 'TEXTO', 25, 'Fortalezas y públicos de cada red.'),
                ('Calendario editorial', 'TEXTO', 20, 'Planificación, frecuencia y formatos por plataforma.'),
                ('Práctica: crear un calendario semanal', 'PRACTICA', 15, 'Calendario para una marca ficticia.'),
            ]),
            ('Módulo 2: Creación de contenido', 120, [
                ('Copywriting para redes', 'TEXTO', 25, 'Hooks, CTAs, storytelling y tono de marca.'),
                ('Diseño visual con Canva y plantillas', 'TEXTO', 25, 'Creación rápida de posts, stories y reels.'),
                ('Video corto: Reels, TikTok y Shorts', 'TEXTO', 30, 'Guion, grabación, edición y tendencias de formato.'),
                ('Herramientas de programación', 'TEXTO', 20, 'Buffer, Hootsuite, Meta Business Suite.'),
                ('Práctica: paquete de contenido', 'PRACTICA', 20, 'Crear 5 posts + 2 stories + 1 reel para una marca.'),
            ]),
            ('Módulo 3: Publicidad y pauta', 110, [
                ('Facebook Ads e Instagram Ads', 'TEXTO', 30, 'Estructura de campaña, segmentación y presupuesto.'),
                ('LinkedIn Ads y TikTok Ads', 'TEXTO', 25, 'Publicidad B2B y audiencias jóvenes.'),
                ('A/B testing y optimización', 'TEXTO', 25, 'Pruebas de creatividad, copy y segmentación.'),
                ('Práctica: configurar una campaña', 'PRACTICA', 30, 'Simular una campaña completa en Ads Manager.'),
            ]),
            ('Módulo 4: Métricas y proyecto final', 100, [
                ('Métricas clave: alcance, engagement, CTR, ROI', 'TEXTO', 25, 'Interpretar datos y tomar decisiones.'),
                ('Reportes y dashboards', 'TEXTO', 20, 'Crear informes mensuales de rendimiento.'),
                ('Community management y crisis', 'TEXTO', 20, 'Gestión de comentarios, DMs y reputación.'),
                ('Proyecto final: estrategia 360°', 'PRACTICA', 35, 'Plan de redes sociales completo para una marca.'),
            ]),
        ],
    ),
    'Google Ads y remarketing': (
        '''Curso especializado en Google Ads (Search, Display, Shopping y YouTube) y estrategias de remarketing para maximizar conversiones. Aprenderás a planificar campañas, investigar keywords con Keyword Planner, escribir anuncios efectivos, configurar extensiones, definir audiencias de remarketing y optimizar el Quality Score. Incluye seguimiento de conversiones con Google Tag Manager, estrategias de puja (manual, CPA, ROAS) y análisis de rendimiento con Google Analytics. Orientado a profesionales de marketing digital que buscan dominar publicidad de pago en el ecosistema de Google.''',
        '''Evaluación: quizzes por módulo (20%), ejercicios prácticos de configuración (25%), proyecto intermedio de campaña Search (25%), proyecto final de campaña multi-red con remarketing (30%). Calificación mínima 70%. Se evalúa correcta configuración, segmentación, calidad de anuncios y análisis.''',
        [
            ('Módulo 1: Fundamentos de Google Ads', 100, [
                ('Bienvenida y ecosistema Google Ads', 'TEXTO', 15, 'Tipos de campañas: Search, Display, Shopping, Video.'),
                ('Keyword research con Keyword Planner', 'TEXTO', 25, 'Búsqueda de palabras clave, volumen, CPC y competencia.'),
                ('Estructura de campaña: cuenta, campañas, grupos, anuncios', 'TEXTO', 25, 'Jerarquía y organización para rendimiento óptimo.'),
                ('Redacción de anuncios y extensiones', 'TEXTO', 25, 'Títulos, descripciones, sitelinks, callouts.'),
                ('Quiz módulo 1', 'QUIZ', 10, 'Preguntas sobre fundamentos.'),
            ]),
            ('Módulo 2: Segmentación y pujas', 110, [
                ('Segmentación: keywords, audiencias y ubicación', 'TEXTO', 25, 'Coincidencia amplia, frase, exacta y negativas.'),
                ('Estrategias de puja: manual, CPA, ROAS', 'TEXTO', 25, 'Cuándo usar cada estrategia y cómo optimizar.'),
                ('Quality Score y relevancia', 'TEXTO', 25, 'CTR esperado, relevancia del anuncio, experiencia de landing.'),
                ('Seguimiento de conversiones', 'TEXTO', 20, 'Google Tag Manager, etiquetas de conversión y eventos.'),
                ('Práctica: crear campaña Search', 'PRACTICA', 15, 'Configurar una campaña de búsqueda desde cero.'),
            ]),
            ('Módulo 3: Display, Shopping y YouTube', 120, [
                ('Campañas de Display: banners y segmentación', 'TEXTO', 30, 'Red de Display, formatos y audiencias.'),
                ('Google Shopping: feed de productos', 'TEXTO', 25, 'Merchant Center, feed XML y optimización.'),
                ('YouTube Ads: formatos y audiencias', 'TEXTO', 25, 'In-stream, bumper, discovery y segmentación.'),
                ('Práctica: campaña Display o Video', 'PRACTICA', 30, 'Configurar y lanzar una campaña no-search.'),
                ('Quiz módulo 3', 'QUIZ', 10, 'Preguntas sobre Display, Shopping y YouTube.'),
            ]),
            ('Módulo 4: Remarketing y proyecto final', 100, [
                ('Remarketing: listas, audiencias y segmentos', 'TEXTO', 25, 'Visitantes del sitio, carritos abandonados, similares.'),
                ('Remarketing dinámico y cross-device', 'TEXTO', 25, 'Anuncios personalizados con productos vistos.'),
                ('Análisis y optimización con Google Analytics', 'TEXTO', 20, 'Atribución, embudos y optimización de campañas.'),
                ('Proyecto final: campaña multi-red con remarketing', 'PRACTICA', 30, 'Plan completo de campaña Search + Display + Remarketing.'),
            ]),
        ],
    ),
    'Excel para finanzas': (
        '''Curso avanzado de Microsoft Excel orientado a profesionales de finanzas, contabilidad y análisis de datos. Cubre desde fórmulas esenciales (BUSCARV, SI, SUMAR.SI, ÍNDICE/COINCIDIR) hasta herramientas avanzadas: tablas dinámicas, gráficos financieros, formato condicional, validación de datos, escenarios y Solver. Incluye modelado financiero: proyecciones de flujo de caja, análisis de sensibilidad, VPN y TIR. El curso aborda también macros básicas (grabación y edición) y dashboards interactivos. Cada módulo tiene ejercicios con datos financieros reales y un proyecto final de modelo financiero completo.''',
        '''Evaluación: quizzes por módulo (15%), ejercicios prácticos de fórmulas y tablas dinámicas (30%), proyecto intermedio de dashboard (25%), proyecto final de modelo financiero (30%). Calificación mínima 70%. Los trabajos se evalúan por corrección de fórmulas, presentación de datos y utilidad del análisis.''',
        [
            ('Módulo 1: Fórmulas y funciones financieras', 110, [
                ('Bienvenida y repaso de Excel', 'TEXTO', 10, 'Interfaz, atajos y buenas prácticas de organización.'),
                ('Fórmulas esenciales: SI, BUSCARV, SUMAR.SI', 'TEXTO', 30, 'Fórmulas condicionales y de búsqueda para finanzas.'),
                ('ÍNDICE/COINCIDIR y fórmulas matriciales', 'TEXTO', 25, 'Búsquedas avanzadas y fórmulas dinámicas.'),
                ('Funciones financieras: VNA, TIR, PAGO, TASA', 'TEXTO', 25, 'Valor presente neto, tasa interna de retorno y amortización.'),
                ('Práctica: análisis de préstamo', 'PRACTICA', 15, 'Tabla de amortización con fórmulas financieras.'),
                ('Quiz módulo 1', 'QUIZ', 5, 'Evaluación de fórmulas.'),
            ]),
            ('Módulo 2: Tablas dinámicas y gráficos', 120, [
                ('Tablas dinámicas: creación y campos', 'TEXTO', 30, 'Origen de datos, filas, columnas, valores y filtros.'),
                ('Segmentación y línea de tiempo', 'TEXTO', 20, 'Filtros interactivos para tablas dinámicas.'),
                ('Gráficos financieros: barras, líneas, cascada', 'TEXTO', 25, 'Visualización de ingresos, gastos y variación.'),
                ('Formato condicional y validación', 'TEXTO', 20, 'Resaltar datos y controlar entradas.'),
                ('Práctica: reporte de ventas', 'PRACTICA', 20, 'Dashboard con tabla dinámica y gráficos.'),
                ('Quiz módulo 2', 'QUIZ', 5, 'Evaluación de tablas dinámicas.'),
            ]),
            ('Módulo 3: Modelado financiero', 130, [
                ('Estructura de un modelo financiero', 'TEXTO', 25, 'Supuestos, estado de resultados, balance y flujo de caja.'),
                ('Proyecciones y escenarios', 'TEXTO', 30, 'Administrador de escenarios, tablas de datos y Solver.'),
                ('Análisis de sensibilidad', 'TEXTO', 25, 'Tablas de datos de una y dos variables.'),
                ('Flujo de caja descontado (DCF)', 'TEXTO', 25, 'Modelo paso a paso con VNA y TIR.'),
                ('Práctica: modelo DCF', 'PRACTICA', 20, 'Construir un modelo de valoración.'),
                ('Quiz módulo 3', 'QUIZ', 5, 'Evaluación de modelado.'),
            ]),
            ('Módulo 4: Dashboards, macros y proyecto final', 100, [
                ('Dashboards interactivos', 'TEXTO', 25, 'Diseño, controles de formulario y gráficos dinámicos.'),
                ('Macros: grabación y edición básica', 'TEXTO', 25, 'Automatizar tareas repetitivas con VBA básico.'),
                ('Buenas prácticas y auditoría de hojas', 'TEXTO', 15, 'Protección, revisión de fórmulas y documentación.'),
                ('Proyecto final: modelo financiero completo', 'PRACTICA', 30, 'Entrega de modelo con supuestos, estados financieros y dashboard.'),
                ('Quiz de cierre', 'QUIZ', 5, 'Evaluación final del curso.'),
            ]),
        ],
    ),
    'Inversión en bolsa': (
        '''Curso avanzado de inversión en mercados bursátiles que cubre desde conceptos fundamentales (acciones, bonos, ETFs, fondos) hasta estrategias de inversión activa y pasiva. Aprenderás análisis fundamental (ratios financieros, estados financieros, valoración por múltiplos y DCF), análisis técnico (tendencias, soportes, resistencias, indicadores), gestión de portafolios (diversificación, correlación, frontera eficiente) y psicología del inversor. Incluye simulación de operaciones en tiempo real y un proyecto final de construcción y seguimiento de portafolio. Orientado a personas con conocimientos básicos de finanzas que desean invertir con criterio.''',
        '''Evaluación: quizzes por módulo (20%), ejercicios de análisis fundamental y técnico (25%), proyecto intermedio de análisis de empresa (25%), proyecto final de portafolio diversificado (30%). Calificación mínima 70%. Se evalúa rigor analítico, fundamentación de decisiones y gestión de riesgo.''',
        [
            ('Módulo 1: Mercados y activos financieros', 100, [
                ('Bienvenida y objetivos', 'TEXTO', 10, 'Qué aprenderás y prerrequisitos del curso.'),
                ('Tipos de activos: acciones, bonos, ETFs, fondos', 'TEXTO', 25, 'Características, riesgo y retorno de cada instrumento.'),
                ('Cómo funciona la bolsa', 'TEXTO', 25, 'Órdenes de compra/venta, brokers, comisiones y horarios.'),
                ('Riesgo y rentabilidad', 'TEXTO', 25, 'Relación riesgo-retorno, volatilidad y horizonte temporal.'),
                ('Quiz módulo 1', 'QUIZ', 15, 'Preguntas sobre mercados y activos.'),
            ]),
            ('Módulo 2: Análisis fundamental', 130, [
                ('Estados financieros: balance, P&G, flujo de caja', 'TEXTO', 30, 'Lectura e interpretación de reportes financieros.'),
                ('Ratios financieros: PER, ROE, margen, deuda', 'TEXTO', 30, 'Indicadores clave para evaluar empresas.'),
                ('Valoración: múltiplos y DCF', 'TEXTO', 30, 'Price/Earnings, EV/EBITDA y flujo de caja descontado.'),
                ('Práctica: analizar una empresa', 'PRACTICA', 30, 'Análisis completo de una empresa cotizada.'),
                ('Quiz módulo 2', 'QUIZ', 10, 'Preguntas sobre análisis fundamental.'),
            ]),
            ('Módulo 3: Análisis técnico', 110, [
                ('Gráficos de velas y tendencias', 'TEXTO', 25, 'Candlestick, líneas de tendencia y soportes/resistencias.'),
                ('Indicadores: medias móviles, RSI, MACD', 'TEXTO', 30, 'Señales de compra/venta y confluencia de indicadores.'),
                ('Patrones chartistas y volumen', 'TEXTO', 25, 'Doble techo, hombro-cabeza-hombro, triángulos y volumen.'),
                ('Práctica: análisis técnico de un activo', 'PRACTICA', 25, 'Identificar tendencias y señales en un gráfico real.'),
                ('Quiz módulo 3', 'QUIZ', 5, 'Preguntas sobre análisis técnico.'),
            ]),
            ('Módulo 4: Portafolio y proyecto final', 120, [
                ('Diversificación y correlación', 'TEXTO', 25, 'Reducir riesgo combinando activos no correlacionados.'),
                ('Frontera eficiente y asignación de activos', 'TEXTO', 25, 'Markowitz, asset allocation por perfil de riesgo.'),
                ('Psicología del inversor y errores comunes', 'TEXTO', 20, 'Sesgos cognitivos: exceso de confianza, aversión a pérdidas.'),
                ('Simulación: operar en plataforma demo', 'PRACTICA', 20, 'Comprar/vender activos en un simulador.'),
                ('Proyecto final: construir un portafolio', 'PRACTICA', 30, 'Portafolio diversificado con justificación y seguimiento.'),
            ]),
        ],
    ),
    'Inglés nivel B1': (
        '''Curso de inglés intermedio (B1) enfocado en desarrollar fluidez conversacional, comprensión auditiva y expresión escrita. Cubre tiempos verbales compuestos (present perfect, past continuous, condicionales), vocabulario temático ampliado (trabajo, viajes, salud, tecnología), expresiones idiomáticas y phrasal verbs frecuentes. Incluye ejercicios de listening con audios reales, reading comprehension, writing estructurado y práctica de speaking con guiones de conversación. El contenido está alineado con el Marco Común Europeo de Referencia (MCER) nivel B1 y prepara para exámenes como PET o IELTS band 4-5.''',
        '''Evaluación: quizzes por unidad (20%), tareas escritas (writing) (25%), ejercicios de listening y reading (25%), examen oral simulado (15%), examen final escrito (15%). Calificación mínima 70%. Retroalimentación en cada entrega escrita y oral.''',
        [
            ('Módulo 1: Present perfect y vocabulario', 100, [
                ('Bienvenida y diagnóstico', 'TEXTO', 10, 'Test de nivel y objetivos del curso B1.'),
                ('Present perfect: experiencias y duración', 'TEXTO', 25, 'Have/has + past participle, for, since, ever, never.'),
                ('Present perfect vs past simple', 'TEXTO', 25, 'Cuándo usar cada tiempo; ejercicios de contraste.'),
                ('Vocabulario: trabajo y carreras', 'TEXTO', 20, 'Profesiones, responsabilidades, entrevistas y CV.'),
                ('Listening: conversaciones laborales', 'TEXTO', 10, 'Ejercicio de comprensión auditiva.'),
                ('Quiz módulo 1', 'QUIZ', 10, 'Preguntas sobre present perfect y vocabulario.'),
            ]),
            ('Módulo 2: Condicionales y expresiones', 110, [
                ('First conditional: situaciones reales', 'TEXTO', 25, 'If + present simple, will + infinitive.'),
                ('Second conditional: hipótesis', 'TEXTO', 25, 'If + past simple, would + infinitive.'),
                ('Phrasal verbs frecuentes', 'TEXTO', 20, 'Look up, give up, turn on, find out y más.'),
                ('Expresiones idiomáticas comunes', 'TEXTO', 20, 'Break the ice, hit the nail on the head, etc.'),
                ('Práctica: writing — email informal', 'PRACTICA', 20, 'Redactar un email describiendo planes futuros.'),
            ]),
            ('Módulo 3: Past continuous y narración', 100, [
                ('Past continuous y past simple juntos', 'TEXTO', 25, 'Acciones en progreso interrumpidas. While/when.'),
                ('Narración: conectores de secuencia', 'TEXTO', 20, 'First, then, after that, finally.'),
                ('Vocabulario: viajes y cultura', 'TEXTO', 20, 'Aeropuerto, hotel, direcciones, experiencias.'),
                ('Reading comprehension: artículo de viajes', 'TEXTO', 15, 'Ejercicio de lectura con preguntas.'),
                ('Práctica: contar una historia', 'PRACTICA', 20, 'Writing o grabación oral narrando un viaje.'),
            ]),
            ('Módulo 4: Revisión, speaking y proyecto final', 110, [
                ('Revisión gramatical integrada', 'TEXTO', 25, 'Mezcla de tiempos, condicionales y phrasal verbs.'),
                ('Vocabulario: salud, tecnología y medio ambiente', 'TEXTO', 20, 'Temas frecuentes en exámenes B1.'),
                ('Speaking practice: role-plays guiados', 'TEXTO', 25, 'Simulación de conversaciones: reservar hotel, entrevista, debate.'),
                ('Mock exam: listening, reading, writing', 'PRACTICA', 30, 'Simulacro tipo PET/IELTS.'),
                ('Quiz final', 'QUIZ', 10, 'Evaluación final del curso.'),
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

    modulos_count = curso.modulos.count()
    if modulos_count >= len(modulos_data):
        return True

    for mod in curso.modulos.all():
        mod.lecciones.all().delete()
        mod.delete()

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
