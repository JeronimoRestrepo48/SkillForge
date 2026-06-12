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
}

export interface Module {
  id: number;
  title: string;
  sort_order: number;
  lessons: Lesson[];
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
