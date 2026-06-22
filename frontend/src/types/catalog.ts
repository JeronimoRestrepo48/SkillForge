export interface Category {
  id: number;
  name: string;
  description?: string;
}

export interface Lesson {
  id: number;
  title: string;
  video_url?: string;
  duration?: number;
  sort_order: number;
  content_type?: string;
}

export interface Module {
  id: number;
  title: string;
  sort_order: number;
  lessons: Lesson[];
  es_examen_modulo?: boolean;
  es_examen_final?: boolean;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  category_id: number;
  price: number;
  status: string;
  nivel_dificultad?: string;
  duracion_horas?: number;
  instructor_id?: number;
  es_certificacion?: boolean;
}

export interface CourseDetail extends Course {
  modules: Module[];
  rating_count: number;
  average_rating: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: number | null;
  previous: number | null;
  results: T[];
}

export interface LessonProgress {
  id: number;
  user_id: number;
  lesson_id: number;
  completed: boolean;
  completed_at: string | null;
}

export interface CourseProgress {
  course_id: number;
  total_lessons: number;
  completed_lessons: number;
  percentage: number;
  completed: boolean;
  completed_lesson_ids: number[];
}

export interface TrayectoriaCurso {
  course_id: number;
  sort_order: number;
  course?: Course;
}

export interface Trayectoria {
  id: number;
  nombre: string;
  descripcion: string | null;
  categoria_general: string | null;
  cursos?: TrayectoriaCurso[];
}

// --- QUIZ & CERTIFICATION TYPES ---

export interface QuizOptionStudentOut {
  id: number;
  texto: string;
}

export interface QuizQuestionStudentOut {
  id: number;
  tipo: string;
  enunciado: string;
  puntaje: number;
  sort_order: number;
  options: QuizOptionStudentOut[];
}

export interface QuizDetailOut {
  id: number;
  lesson_id: number;
  titulo: string;
  puntaje_minimo_aprobacion: number;
  questions: QuizQuestionStudentOut[];
}

export interface QuizAttemptSubmitItem {
  question_id: number;
  respuesta_texto?: string;
  selected_option_id?: number;
}

export interface QuizAttemptSubmit {
  respuestas: QuizAttemptSubmitItem[];
}

export interface QuizAttemptAnswerOut {
  question_id: number;
  respuesta_texto?: string;
  selected_option_id?: number;
  similitud?: number;
  puntaje_obtenido: number;
  es_correcta?: boolean;
}

export interface QuizAttemptResultOut {
  id: number;
  quiz_id: number;
  user_id: number;
  puntaje_obtenido: number;
  puntaje_maximo: number;
  porcentaje: number;
  aprobado: boolean;
  created_at: string;
  answers: QuizAttemptAnswerOut[];
}

export interface CertificationModuleStatus {
  module_id: number;
  title: string;
  sort_order: number;
  es_examen_modulo: boolean;
  es_examen_final: boolean;
  bloqueado: boolean;
  aprobado: boolean | null;
}

export interface CertificationProgressOut {
  course_id: number;
  modules: CertificationModuleStatus[];
  certificado_disponible: boolean;
}
