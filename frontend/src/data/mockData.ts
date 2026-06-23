// ═══════════════════════════════════════════════════════════════════════════════
// SKILLFORGE — DEMO MOCK DATA
// Datos estáticos realistas para modo demo (deploy en Vercel sin backend)
// ═══════════════════════════════════════════════════════════════════════════════

import type { Course, CourseDetail, Category, Lesson, CourseProgress, Trayectoria } from '../types/catalog';
import type { UserResponse } from '../types/auth';
import type { Enrollment } from '../types/transactions';
import type { Certificate } from '../types/certificates';

// ── Usuario Demo ──────────────────────────────────────────────────────────────
export const DEMO_USER: UserResponse = {
  id: 1,
  username: 'cristobal.rodriguez',
  email: 'cristobal.rodriguez@skillforge.dev',
  role: 'student',
  nombre_completo: 'Cristobal Rodriguez',
  telefono: '+57 300 123 4567',
  ciudad: 'Medellín',
  pais: 'Colombia',
  created_at: '2025-08-15T10:30:00Z',
};

// ── Categorías ────────────────────────────────────────────────────────────────
export const DEMO_CATEGORIES: Category[] = [
  { id: 1, name: 'Backend', description: 'Desarrollo del lado del servidor' },
  { id: 2, name: 'Frontend', description: 'Interfaces web modernas' },
  { id: 3, name: 'Data Science', description: 'Análisis de datos y machine learning' },
  { id: 4, name: 'DevOps', description: 'Infraestructura y despliegue continuo' },
  { id: 5, name: 'Diseño UX/UI', description: 'Experiencia e interfaz de usuario' },
  { id: 6, name: 'Mobile', description: 'Desarrollo de aplicaciones móviles' },
  { id: 7, name: 'Cloud Computing', description: 'Servicios en la nube' },
  { id: 8, name: 'IA / Machine Learning', description: 'Inteligencia artificial aplicada' },
];

// ── Lecciones helper ──────────────────────────────────────────────────────────
const makeLessons = (moduleId: number, titles: string[]): Lesson[] =>
  titles.map((title, i) => ({
    id: moduleId * 100 + i + 1,
    title,
    video_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    duration: 10 + Math.floor(Math.random() * 25),
    sort_order: i + 1,
    content_type: title.toLowerCase().includes('quiz') ? 'QUIZ' : 'VIDEO',
  }));

// ── Cursos con módulos y lecciones ────────────────────────────────────────────
export const DEMO_COURSES_DETAIL: CourseDetail[] = [
  {
    id: 1,
    title: 'Python Fundamentals',
    description: 'Domina los fundamentos de Python desde cero. Aprende tipos de datos, estructuras de control, funciones, POO y manejo de archivos con proyectos prácticos guiados.',
    category_id: 1,
    price: 89000,
    status: 'PUBLISHED',
    nivel_dificultad: 'PRINCIPIANTE',
    duracion_horas: 24,
    instructor_id: 2,
    es_certificacion: false,
    rating_count: 47,
    average_rating: 4.7,
    modules: [
      { id: 1, title: 'Introducción a Python', sort_order: 1, lessons: makeLessons(1, ['Instalación y entorno', 'Variables y tipos de datos', 'Operadores y expresiones', 'Quiz: Fundamentos']) },
      { id: 2, title: 'Control de flujo', sort_order: 2, lessons: makeLessons(2, ['Condicionales if/elif/else', 'Bucles for y while', 'Comprensiones de lista', 'Ejercicio práctico']) },
      { id: 3, title: 'Funciones y módulos', sort_order: 3, lessons: makeLessons(3, ['Definición de funciones', 'Parámetros y retorno', 'Módulos y paquetes', 'Proyecto: Calculadora CLI']) },
      { id: 4, title: 'Programación Orientada a Objetos', sort_order: 4, lessons: makeLessons(4, ['Clases y objetos', 'Herencia y polimorfismo', 'Métodos mágicos', 'Quiz: POO en Python']) },
    ],
  },
  {
    id: 2,
    title: 'React & TypeScript Avanzado',
    description: 'Construye aplicaciones React modernas con TypeScript, hooks personalizados, gestión de estado con React Query y patrones de arquitectura escalable.',
    category_id: 2,
    price: 129000,
    status: 'PUBLISHED',
    nivel_dificultad: 'AVANZADO',
    duracion_horas: 36,
    instructor_id: 2,
    es_certificacion: true,
    rating_count: 32,
    average_rating: 4.9,
    modules: [
      { id: 5, title: 'TypeScript para React', sort_order: 1, lessons: makeLessons(5, ['Tipos e interfaces', 'Generics en componentes', 'Type guards y utilidades', 'Quiz: TypeScript']) },
      { id: 6, title: 'Hooks avanzados', sort_order: 2, lessons: makeLessons(6, ['useReducer vs useState', 'Custom hooks', 'useCallback y useMemo', 'Patrones de composición']) },
      { id: 7, title: 'Estado del servidor', sort_order: 3, lessons: makeLessons(7, ['React Query fundamentals', 'Mutations y cache', 'Optimistic updates', 'Proyecto: Dashboard']) },
    ],
  },
  {
    id: 3,
    title: 'Arquitectura de Microservicios',
    description: 'Diseña sistemas distribuidos escalables. Aprende patrones como Strangler Fig, Event-Driven Architecture, CQRS y deploy con Docker Compose y Kubernetes.',
    category_id: 4,
    price: 150000,
    status: 'PUBLISHED',
    nivel_dificultad: 'AVANZADO',
    duracion_horas: 40,
    instructor_id: 2,
    es_certificacion: true,
    rating_count: 28,
    average_rating: 4.8,
    modules: [
      { id: 8, title: 'Fundamentos de microservicios', sort_order: 1, lessons: makeLessons(8, ['Monolito vs microservicios', 'Bounded contexts (DDD)', 'API Gateway pattern', 'Quiz: Conceptos']) },
      { id: 9, title: 'Comunicación entre servicios', sort_order: 2, lessons: makeLessons(9, ['REST vs gRPC vs mensajería', 'Event Bus con Redis Streams', 'Sagas y consistencia eventual', 'Ejercicio: Event-driven']) },
      { id: 10, title: 'Despliegue y observabilidad', sort_order: 3, lessons: makeLessons(10, ['Docker Compose multi-servicio', 'CI/CD con GitHub Actions', 'Logs centralizados', 'Proyecto: Deploy completo']) },
    ],
  },
  {
    id: 4,
    title: 'Flask para APIs RESTful',
    description: 'Crea APIs robustas y bien documentadas con Flask. Incluye autenticación JWT, validación con Pydantic, migraciones con Alembic y testing con pytest.',
    category_id: 1,
    price: 95000,
    status: 'PUBLISHED',
    nivel_dificultad: 'INTERMEDIO',
    duracion_horas: 28,
    instructor_id: 2,
    es_certificacion: false,
    rating_count: 35,
    average_rating: 4.5,
    modules: [
      { id: 11, title: 'Flask desde cero', sort_order: 1, lessons: makeLessons(11, ['Hola Mundo con Flask', 'Rutas y blueprints', 'Manejo de errores', 'Quiz: Flask basics']) },
      { id: 12, title: 'Base de datos y ORM', sort_order: 2, lessons: makeLessons(12, ['SQLAlchemy setup', 'Modelos y relaciones', 'Migraciones con Alembic', 'CRUD completo']) },
      { id: 13, title: 'Seguridad y documentación', sort_order: 3, lessons: makeLessons(13, ['JWT Authentication', 'Validación con Pydantic', 'OpenAPI / Swagger', 'Proyecto: API productiva']) },
    ],
  },
  {
    id: 5,
    title: 'Machine Learning con Python',
    description: 'Aprende los algoritmos fundamentales de Machine Learning: regresión, clasificación, clustering y redes neuronales con scikit-learn y TensorFlow.',
    category_id: 8,
    price: 175000,
    status: 'PUBLISHED',
    nivel_dificultad: 'AVANZADO',
    duracion_horas: 48,
    instructor_id: 2,
    es_certificacion: true,
    rating_count: 19,
    average_rating: 4.6,
    modules: [
      { id: 14, title: 'Fundamentos de ML', sort_order: 1, lessons: makeLessons(14, ['¿Qué es Machine Learning?', 'Tipos de aprendizaje', 'Preparación de datos', 'Quiz: Conceptos ML']) },
      { id: 15, title: 'Algoritmos supervisados', sort_order: 2, lessons: makeLessons(15, ['Regresión lineal y logística', 'Árboles de decisión', 'Random Forest y SVM', 'Ejercicio: Clasificación']) },
      { id: 16, title: 'Deep Learning intro', sort_order: 3, lessons: makeLessons(16, ['Redes neuronales', 'TensorFlow y Keras', 'CNN para imágenes', 'Proyecto: Clasificador']) },
    ],
  },
  {
    id: 6,
    title: 'Docker & Kubernetes para Developers',
    description: 'Conteneriza tus aplicaciones con Docker y orquéstalas con Kubernetes. Incluye Docker Compose, Helm charts, y despliegue en AWS EKS.',
    category_id: 4,
    price: 135000,
    status: 'PUBLISHED',
    nivel_dificultad: 'INTERMEDIO',
    duracion_horas: 32,
    instructor_id: 2,
    es_certificacion: false,
    rating_count: 22,
    average_rating: 4.4,
    modules: [
      { id: 17, title: 'Docker fundamentals', sort_order: 1, lessons: makeLessons(17, ['Instalación de Docker', 'Imágenes y contenedores', 'Dockerfile best practices', 'Docker Compose']) },
      { id: 18, title: 'Kubernetes esencial', sort_order: 2, lessons: makeLessons(18, ['Pods, Services, Deployments', 'ConfigMaps y Secrets', 'Ingress y networking', 'Helm charts']) },
      { id: 19, title: 'Deploy en producción', sort_order: 3, lessons: makeLessons(19, ['AWS EKS setup', 'CI/CD con K8s', 'Monitoreo con Prometheus', 'Proyecto: Full deploy']) },
    ],
  },
  {
    id: 7,
    title: 'Diseño UX/UI con Figma',
    description: 'Domina Figma para diseñar interfaces profesionales. Aprende sistemas de diseño, prototipado interactivo, design tokens y handoff a desarrollo.',
    category_id: 5,
    price: 79000,
    status: 'PUBLISHED',
    nivel_dificultad: 'PRINCIPIANTE',
    duracion_horas: 20,
    instructor_id: 2,
    es_certificacion: false,
    rating_count: 41,
    average_rating: 4.8,
    modules: [
      { id: 20, title: 'Fundamentos de Figma', sort_order: 1, lessons: makeLessons(20, ['Interfaz y herramientas', 'Auto Layout', 'Componentes y variantes', 'Quiz: Figma basics']) },
      { id: 21, title: 'Sistemas de diseño', sort_order: 2, lessons: makeLessons(21, ['Design tokens', 'Librería de componentes', 'Estilos y tipografía', 'Proyecto: Design system']) },
    ],
  },
  {
    id: 8,
    title: 'Next.js 14 Full-Stack',
    description: 'Construye aplicaciones full-stack con Next.js 14, App Router, Server Components, Server Actions y despliegue en Vercel.',
    category_id: 2,
    price: 145000,
    status: 'PUBLISHED',
    nivel_dificultad: 'INTERMEDIO',
    duracion_horas: 34,
    instructor_id: 2,
    es_certificacion: false,
    rating_count: 15,
    average_rating: 4.7,
    modules: [
      { id: 22, title: 'App Router y RSC', sort_order: 1, lessons: makeLessons(22, ['App Router vs Pages Router', 'Server Components', 'Loading y error states', 'Quiz: RSC']) },
      { id: 23, title: 'Data fetching y actions', sort_order: 2, lessons: makeLessons(23, ['fetch con cache', 'Server Actions', 'Revalidación', 'Proyecto: Blog full-stack']) },
    ],
  },
  {
    id: 9,
    title: 'React Native & Expo',
    description: 'Crea apps móviles nativas para iOS y Android con React Native y Expo. Incluye navegación, estado, APIs nativas y publicación en stores.',
    category_id: 6,
    price: 119000,
    status: 'PUBLISHED',
    nivel_dificultad: 'INTERMEDIO',
    duracion_horas: 30,
    instructor_id: 2,
    es_certificacion: false,
    rating_count: 18,
    average_rating: 4.3,
    modules: [
      { id: 24, title: 'Expo y componentes', sort_order: 1, lessons: makeLessons(24, ['Setup con Expo', 'Componentes nativos', 'Estilos y layout', 'Navegación con React Navigation']) },
      { id: 25, title: 'APIs y publicación', sort_order: 2, lessons: makeLessons(25, ['Consumo de APIs REST', 'AsyncStorage y estado', 'Build y deploy', 'Proyecto: App productiva']) },
    ],
  },
];

// Cursos simplificados (sin modules) para listados
export const DEMO_COURSES: Course[] = DEMO_COURSES_DETAIL.map(({ modules, rating_count, average_rating, ...c }) => c);

// ── Reseñas ───────────────────────────────────────────────────────────────────
export const DEMO_REVIEWS: Record<number, any[]> = {
  1: [
    { id: 1, course_id: 1, user_id: 5, score: 5, comment: 'Excelente curso para empezar con Python. Los ejercicios prácticos son muy claros y el instructor explica todo paso a paso.', created_at: '2026-03-15T14:30:00Z' },
    { id: 2, course_id: 1, user_id: 8, score: 4, comment: 'Muy buen contenido, me ayudó a entender POO finalmente. Solo le faltaría más proyectos al final.', created_at: '2026-04-02T09:15:00Z' },
    { id: 3, course_id: 1, user_id: 12, score: 5, comment: 'Lo recomiendo al 100%. Pasé de no saber nada a escribir scripts funcionales en menos de un mes.', created_at: '2026-05-20T18:45:00Z' },
  ],
  2: [
    { id: 4, course_id: 2, user_id: 3, score: 5, comment: 'El mejor curso de React con TypeScript que he encontrado. Los patrones de hooks avanzados son oro puro.', created_at: '2026-02-10T11:00:00Z' },
    { id: 5, course_id: 2, user_id: 7, score: 5, comment: 'React Query cambió mi forma de manejar estado del servidor. Contenido de nivel profesional.', created_at: '2026-04-18T16:20:00Z' },
  ],
  3: [
    { id: 6, course_id: 3, user_id: 4, score: 5, comment: 'Increíble profundidad. Aprendí Event-Driven Architecture y ya lo apliqué en mi trabajo.', created_at: '2026-01-25T10:30:00Z' },
    { id: 7, course_id: 3, user_id: 9, score: 4, comment: 'Muy completo. La sección de Docker Compose multi-servicio es exactamente lo que necesitaba.', created_at: '2026-03-08T14:45:00Z' },
  ],
  4: [
    { id: 8, course_id: 4, user_id: 6, score: 5, comment: 'Flask nunca me había parecido tan claro. Las migraciones con Alembic fueron revelación.', created_at: '2026-05-01T08:00:00Z' },
    { id: 9, course_id: 4, user_id: 11, score: 4, comment: 'Buen curso, aprendí a documentar APIs correctamente con Swagger. Muy práctico.', created_at: '2026-06-10T20:30:00Z' },
  ],
  5: [
    { id: 10, course_id: 5, user_id: 2, score: 5, comment: 'La mejor introducción a ML que he encontrado en español. El proyecto de clasificador fue genial.', created_at: '2026-04-22T13:15:00Z' },
  ],
};

// ── Trayectorias ──────────────────────────────────────────────────────────────
export const DEMO_TRAYECTORIAS: Trayectoria[] = [
  {
    id: 1,
    nombre: 'Full-Stack Python Developer',
    descripcion: 'Domina el desarrollo full-stack con Python. Desde los fundamentos del lenguaje hasta APIs RESTful con Flask y arquitectura de microservicios.',
    categoria_general: 'Backend',
    cursos: [
      { course_id: 1, sort_order: 1, course: DEMO_COURSES[0] },
      { course_id: 4, sort_order: 2, course: DEMO_COURSES[3] },
      { course_id: 3, sort_order: 3, course: DEMO_COURSES[2] },
    ],
  },
  {
    id: 2,
    nombre: 'Frontend Engineer',
    descripcion: 'Conviértete en un ingeniero frontend profesional. Aprende React avanzado con TypeScript, Next.js full-stack y diseño UX/UI.',
    categoria_general: 'Frontend',
    cursos: [
      { course_id: 2, sort_order: 1, course: DEMO_COURSES[1] },
      { course_id: 8, sort_order: 2, course: DEMO_COURSES[7] },
      { course_id: 7, sort_order: 3, course: DEMO_COURSES[6] },
    ],
  },
  {
    id: 3,
    nombre: 'Cloud & DevOps Engineer',
    descripcion: 'Aprende a desplegar y operar sistemas en la nube. Docker, Kubernetes, CI/CD y arquitectura de microservicios en AWS.',
    categoria_general: 'DevOps',
    cursos: [
      { course_id: 6, sort_order: 1, course: DEMO_COURSES[5] },
      { course_id: 3, sort_order: 2, course: DEMO_COURSES[2] },
    ],
  },
  {
    id: 4,
    nombre: 'Data & IA Track',
    descripcion: 'Inicia tu camino en ciencia de datos e inteligencia artificial. Desde Python fundamentals hasta modelos de Machine Learning.',
    categoria_general: 'IA / Machine Learning',
    cursos: [
      { course_id: 1, sort_order: 1, course: DEMO_COURSES[0] },
      { course_id: 5, sort_order: 2, course: DEMO_COURSES[4] },
    ],
  },
];

// ── Inscripciones del usuario demo ────────────────────────────────────────────
export const DEMO_ENROLLMENTS: Enrollment[] = [
  { id: 1, user_id: 1, course_id: 1, order_id: 1, status: 'ACTIVA', enrolled_at: '2026-01-15T10:00:00Z' },
  { id: 2, user_id: 1, course_id: 2, order_id: 2, status: 'ACTIVA', enrolled_at: '2026-02-20T14:30:00Z' },
  { id: 3, user_id: 1, course_id: 3, order_id: 3, status: 'ACTIVA', enrolled_at: '2026-03-10T09:00:00Z' },
  { id: 4, user_id: 1, course_id: 5, order_id: 4, status: 'ACTIVA', enrolled_at: '2026-04-05T16:00:00Z' },
];

// ── Progreso por curso ────────────────────────────────────────────────────────
export const DEMO_PROGRESS: Record<number, CourseProgress> = {
  1: {  // Python Fundamentals — completado
    course_id: 1,
    total_lessons: 16,
    completed_lessons: 16,
    percentage: 100,
    completed: true,
    completed_lesson_ids: Array.from({ length: 16 }, (_, i) => 100 + i + 1).concat(
      Array.from({ length: 16 }, (_, i) => 200 + i + 1),
      Array.from({ length: 16 }, (_, i) => 300 + i + 1),
      Array.from({ length: 16 }, (_, i) => 400 + i + 1)
    ).slice(0, 16),
  },
  2: {  // React & TypeScript — 65%
    course_id: 2,
    total_lessons: 12,
    completed_lessons: 8,
    percentage: 65,
    completed: false,
    completed_lesson_ids: [501, 502, 503, 504, 601, 602, 603, 604],
  },
  3: {  // Arquitectura de Microservicios — 30%
    course_id: 3,
    total_lessons: 12,
    completed_lessons: 4,
    percentage: 30,
    completed: false,
    completed_lesson_ids: [801, 802, 803, 804],
  },
  5: {  // Machine Learning — 10%
    course_id: 5,
    total_lessons: 12,
    completed_lessons: 1,
    percentage: 10,
    completed: false,
    completed_lesson_ids: [1401],
  },
};

// ── Certificados ──────────────────────────────────────────────────────────────
export const DEMO_CERTIFICATES: Certificate[] = [
  {
    id: 1,
    user_id: 1,
    course_id: 1,
    course_title: 'Python Fundamentals',
    student_name: 'Cristobal Rodriguez',
    numero_certificado: 'SF-2026-PY001',
    codigo_verificacion: 'a3f7b2c1-4d5e-6f7a-8b9c-0d1e2f3a4b5c',
    fecha_emision: '2026-04-01T00:00:00Z',
    pdf_url: '#',
    plantilla: 'default',
  },
  {
    id: 2,
    user_id: 1,
    course_id: 2,
    course_title: 'React & TypeScript Avanzado',
    student_name: 'Cristobal Rodriguez',
    numero_certificado: 'SF-2026-RTS002',
    codigo_verificacion: 'b4e8c3d2-5f6a-7b8c-9d0e-1f2a3b4c5d6e',
    fecha_emision: '2026-06-15T00:00:00Z',
    pdf_url: '#',
    plantilla: 'default',
  },
];

// ── Anuncios ──────────────────────────────────────────────────────────────────
export const DEMO_ANNOUNCEMENTS: any[] = [
  {
    id: 1,
    titulo: '🚀 Nuevas certificaciones disponibles',
    contenido: 'Ahora puedes obtener certificados verificables en nuestros cursos de React & TypeScript y Arquitectura de Microservicios.',
    activo: true,
    created_at: '2026-06-01T00:00:00Z',
  },
  {
    id: 2,
    titulo: '📚 Trayectorias de aprendizaje',
    contenido: 'Sigue rutas de aprendizaje curadas por expertos para convertirte en Full-Stack Developer, Frontend Engineer o Cloud Engineer.',
    activo: true,
    created_at: '2026-05-15T00:00:00Z',
  },
];

// ── Instructor profile mock ──────────────────────────────────────────────────
export const DEMO_INSTRUCTOR_PROFILE = {
  id: 1,
  user_id: 2,
  bio: 'Ingeniero de software con más de 8 años de experiencia en desarrollo backend, arquitectura de microservicios y cloud computing. Apasionado por la enseñanza y las buenas prácticas.',
  carrera: 'Ingeniería de Sistemas',
  estudios: 'Maestría en Arquitectura de Software — Universidad EAFIT',
  linkedin_url: 'https://linkedin.com/in/skillforge-instructor',
  sitio_web: 'https://skillforge.dev',
  avatar_url: null,
};
