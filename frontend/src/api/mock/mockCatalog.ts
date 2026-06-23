// Mock implementation of catalogApi for demo mode
import {
  DEMO_COURSES,
  DEMO_COURSES_DETAIL,
  DEMO_CATEGORIES,
  DEMO_REVIEWS,
  DEMO_TRAYECTORIAS,
  DEMO_PROGRESS,
  DEMO_ANNOUNCEMENTS,
} from '../../data/mockData';
import type { Course, CourseDetail, Category, PaginatedResponse, CourseProgress, LessonProgress, Trayectoria } from '../../types/catalog';

// Simulate network delay for realism
const delay = (ms = 300) => new Promise(r => setTimeout(r, ms));

export const mockCatalogApi = {
  getCourses: async (params?: { q?: string; categoria?: number; page?: number; page_size?: number }): Promise<PaginatedResponse<Course>> => {
    await delay(200);
    let filtered = [...DEMO_COURSES];
    if (params?.q) {
      const q = params.q.toLowerCase();
      filtered = filtered.filter(c => c.title.toLowerCase().includes(q) || c.description.toLowerCase().includes(q));
    }
    if (params?.categoria) {
      filtered = filtered.filter(c => c.category_id === params.categoria);
    }
    const page = params?.page || 1;
    const pageSize = params?.page_size || 6;
    const start = (page - 1) * pageSize;
    const paged = filtered.slice(start, start + pageSize);
    return {
      count: filtered.length,
      next: start + pageSize < filtered.length ? page + 1 : null,
      previous: page > 1 ? page - 1 : null,
      results: paged,
    };
  },

  getMyCourses: async (): Promise<Course[]> => {
    await delay();
    return DEMO_COURSES.slice(0, 3);
  },

  getCourseDetail: async (courseId: number): Promise<CourseDetail> => {
    await delay(250);
    const course = DEMO_COURSES_DETAIL.find(c => c.id === courseId);
    if (!course) throw new Error('Curso no encontrado');
    return course;
  },

  createCourse: async (data: any): Promise<Course> => {
    await delay();
    return { id: 100, ...data, status: 'DRAFT' } as Course;
  },

  getCategories: async (_params?: any): Promise<PaginatedResponse<Category>> => {
    await delay(100);
    return { count: DEMO_CATEGORIES.length, next: null, previous: null, results: DEMO_CATEGORIES };
  },

  completeLesson: async (lessonId: number): Promise<LessonProgress> => {
    await delay();
    return { id: lessonId, user_id: 1, lesson_id: lessonId, completed: true, completed_at: new Date().toISOString() };
  },

  getCourseProgress: async (courseId: number): Promise<CourseProgress> => {
    await delay(150);
    return DEMO_PROGRESS[courseId] || {
      course_id: courseId, total_lessons: 12, completed_lessons: 0, percentage: 0, completed: false, completed_lesson_ids: [],
    };
  },

  updateCourse: async (courseId: number, data: any): Promise<Course> => {
    await delay();
    return { id: courseId, ...data } as Course;
  },

  createModule: async (_courseId: number, data: any): Promise<any> => {
    await delay();
    return { id: 100, ...data };
  },

  createLesson: async (_moduleId: number, data: any): Promise<any> => {
    await delay();
    return { id: 200, ...data };
  },

  deleteModule: async (): Promise<void> => { await delay(); },
  deleteLesson: async (): Promise<void> => { await delay(); },

  getTrayectorias: async (): Promise<Trayectoria[]> => {
    await delay(200);
    return DEMO_TRAYECTORIAS;
  },

  getTrayectoriaDetail: async (id: number): Promise<Trayectoria> => {
    await delay(250);
    const t = DEMO_TRAYECTORIAS.find(t => t.id === id);
    if (!t) throw new Error('Trayectoria no encontrada');
    return t;
  },

  createTrayectoria: async (data: any): Promise<any> => {
    await delay();
    return { id: 100, ...data };
  },
  updateTrayectoria: async (id: number, data: any): Promise<any> => {
    await delay();
    return { id, ...data };
  },
  deleteTrayectoria: async (): Promise<void> => { await delay(); },
  addCourseToTrayectoria: async (_id: number, data: any): Promise<any> => {
    await delay();
    return data;
  },
  removeCourseFromTrayectoria: async (): Promise<void> => { await delay(); },

  getCertificationProgress: async (courseId: number): Promise<any> => {
    await delay();
    const course = DEMO_COURSES_DETAIL.find(c => c.id === courseId);
    if (!course) return { course_id: courseId, modules: [], certificado_disponible: false };
    return {
      course_id: courseId,
      modules: course.modules.map(m => ({
        module_id: m.id,
        title: m.title,
        sort_order: m.sort_order,
        es_examen_modulo: false,
        es_examen_final: false,
        bloqueado: false,
        aprobado: DEMO_PROGRESS[courseId]?.completed || false,
      })),
      certificado_disponible: DEMO_PROGRESS[courseId]?.completed || false,
    };
  },

  getQuizDetails: async (lessonId: number): Promise<any> => {
    await delay();
    return {
      id: lessonId,
      lesson_id: lessonId,
      titulo: 'Quiz de práctica',
      puntaje_minimo_aprobacion: 60,
      questions: [
        { id: 1, tipo: 'OPCION_MULTIPLE', enunciado: 'Pregunta de ejemplo', puntaje: 25, sort_order: 1, options: [
          { id: 1, texto: 'Opción A' }, { id: 2, texto: 'Opción B' }, { id: 3, texto: 'Opción C' }, { id: 4, texto: 'Opción D' },
        ]},
      ],
    };
  },

  submitQuizAttempt: async (_quizId: number, _data: any): Promise<any> => {
    await delay(500);
    return {
      id: 1, quiz_id: _quizId, user_id: 1, puntaje_obtenido: 85, puntaje_maximo: 100, porcentaje: 85, aprobado: true,
      created_at: new Date().toISOString(), answers: [],
    };
  },

  getQuizAttempts: async (_quizId: number): Promise<any[]> => {
    await delay();
    return [];
  },

  createQuiz: async (_lessonId: number, data: any): Promise<any> => {
    await delay();
    return { id: 100, ...data };
  },

  updateModule: async (_courseId: number, _moduleId: number, data: any): Promise<any> => {
    await delay();
    return { id: _moduleId, ...data };
  },

  getReviews: async (courseId: number): Promise<any[]> => {
    await delay(200);
    return DEMO_REVIEWS[courseId] || [];
  },

  submitReview: async (_courseId: number, data: any): Promise<any> => {
    await delay();
    return { id: 100, course_id: _courseId, user_id: 1, ...data, created_at: new Date().toISOString() };
  },

  getFeaturedCourses: async (): Promise<Course[]> => {
    await delay(200);
    return [...DEMO_COURSES].sort(() => Math.random() - 0.5).slice(0, 5);
  },

  getAnnouncements: async (): Promise<any[]> => {
    await delay(100);
    return DEMO_ANNOUNCEMENTS;
  },
};
