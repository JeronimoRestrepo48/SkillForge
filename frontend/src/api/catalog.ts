import api from './axios';
import { 
  Course, 
  CourseDetail, 
  Category, 
  PaginatedResponse, 
  LessonProgress, 
  CourseProgress 
} from '../types/catalog';

const _realCatalogApi = {
  // Listar cursos con búsqueda opcional, filtrado y paginación
  getCourses: async (params?: { q?: string; categoria?: number; page?: number; page_size?: number }): Promise<PaginatedResponse<Course>> => {
    const response = await api.get<PaginatedResponse<Course>>('/catalog/courses', { params });
    return response.data;
  },

  // Obtener los cursos creados por el instructor actual
  getMyCourses: async (): Promise<Course[]> => {
    const response = await api.get<Course[]>('/catalog/my-courses');
    return response.data;
  },

  // Detalle de un curso específico por ID
  getCourseDetail: async (courseId: number): Promise<CourseDetail> => {
    const response = await api.get<CourseDetail>(`/catalog/courses/${courseId}`);
    return response.data;
  },

  // Crear un nuevo curso
  createCourse: async (data: { title: string; description: string; category_id: number; price: number; nivel_dificultad: string; duracion_horas: number }): Promise<Course> => {
    const response = await api.post<Course>('/catalog/courses', data);
    return response.data;
  },

  // Listar todas las categorías disponibles
  getCategories: async (params?: { page?: number; page_size?: number }): Promise<PaginatedResponse<Category>> => {
    const response = await api.get<PaginatedResponse<Category>>('/catalog/categories', { params });
    return response.data;
  },

  // Marcar una lección específica como completada
  completeLesson: async (lessonId: number): Promise<LessonProgress> => {
    const response = await api.post<LessonProgress>(`/catalog/lessons/${lessonId}/complete`);
    return response.data;
  },

  // Obtener el progreso general de un curso para el estudiante logueado
  getCourseProgress: async (courseId: number): Promise<CourseProgress> => {
    const response = await api.get<CourseProgress>(`/catalog/courses/${courseId}/progress`);
    return response.data;
  },

  // Actualizar un curso
  updateCourse: async (courseId: number, data: { title: string; description: string; category_id: number; price: number; nivel_dificultad: string; duracion_horas: number; status: string }): Promise<Course> => {
    const response = await api.put<Course>(`/catalog/courses/${courseId}`, data);
    return response.data;
  },

  // Crear un módulo
  createModule: async (courseId: number, data: { title: string; sort_order: number }): Promise<any> => {
    const response = await api.post(`/catalog/courses/${courseId}/modules`, data);
    return response.data;
  },

  // Crear una lección
  createLesson: async (moduleId: number, data: { title: string; content_type: string; content?: string; sort_order: number; duration_minutes: number }): Promise<any> => {
    const response = await api.post(`/catalog/modules/${moduleId}/lessons`, data);
    return response.data;
  },

  // Eliminar un módulo
  deleteModule: async (courseId: number, moduleId: number): Promise<void> => {
    await api.delete(`/catalog/courses/${courseId}/modules/${moduleId}`);
  },

  // Eliminar una lección
  deleteLesson: async (moduleId: number, lessonId: number): Promise<void> => {
    await api.delete(`/catalog/modules/${moduleId}/lessons/${lessonId}`);
  },

  // Trayectorias
  getTrayectorias: async (): Promise<any> => {
    const response = await api.get('/catalog/trayectorias');
    return response.data;
  },
  getTrayectoriaDetail: async (id: number): Promise<any> => {
    const response = await api.get(`/catalog/trayectorias/${id}`);
    return response.data;
  },
  createTrayectoria: async (data: any): Promise<any> => {
    const response = await api.post('/catalog/trayectorias', data);
    return response.data;
  },
  updateTrayectoria: async (id: number, data: any): Promise<any> => {
    const response = await api.put(`/catalog/trayectorias/${id}`, data);
    return response.data;
  },
  deleteTrayectoria: async (id: number): Promise<void> => {
    await api.delete(`/catalog/trayectorias/${id}`);
  },
  addCourseToTrayectoria: async (id: number, data: any): Promise<any> => {
    const response = await api.post(`/catalog/trayectorias/${id}/cursos`, data);
    return response.data;
  },
  removeCourseFromTrayectoria: async (id: number, courseId: number): Promise<void> => {
    await api.delete(`/catalog/trayectorias/${id}/cursos/${courseId}`);
  },

  // Certifications and Quizzes
  getCertificationProgress: async (courseId: number): Promise<import('../types/catalog').CertificationProgressOut> => {
    const response = await api.get<import('../types/catalog').CertificationProgressOut>(`/catalog/courses/${courseId}/certification-progress`);
    return response.data;
  },
  getQuizDetails: async (lessonId: number): Promise<import('../types/catalog').QuizDetailOut> => {
    const response = await api.get<import('../types/catalog').QuizDetailOut>(`/catalog/lessons/${lessonId}/quiz`);
    return response.data;
  },
  submitQuizAttempt: async (quizId: number, data: import('../types/catalog').QuizAttemptSubmit): Promise<import('../types/catalog').QuizAttemptResultOut> => {
    const response = await api.post<import('../types/catalog').QuizAttemptResultOut>(`/catalog/quizzes/${quizId}/attempts`, data);
    return response.data;
  },
  getQuizAttempts: async (quizId: number): Promise<import('../types/catalog').QuizAttemptResultOut[]> => {
    const response = await api.get<import('../types/catalog').QuizAttemptResultOut[]>(`/catalog/quizzes/${quizId}/attempts/me`);
    return response.data;
  },
  createQuiz: async (lessonId: number, data: any): Promise<any> => {
    const response = await api.post(`/catalog/lessons/${lessonId}/quiz`, data);
    return response.data;
  },
  updateModule: async (courseId: number, moduleId: number, data: any): Promise<any> => {
    const response = await api.put(`/catalog/courses/${courseId}/modules/${moduleId}`, data);
    return response.data;
  },
  getReviews: async (courseId: number): Promise<any[]> => {
    const response = await api.get(`/catalog/courses/${courseId}/reviews`);
    return response.data.results || [];
  },
  submitReview: async (courseId: number, data: { score: number; comment: string }): Promise<any> => {
    const response = await api.post(`/catalog/courses/${courseId}/review`, data);
    return response.data;
  },

  // Cursos destacados aleatorios para el hero slider
  getFeaturedCourses: async (): Promise<Course[]> => {
    const response = await api.get<PaginatedResponse<Course>>('/catalog/courses', { params: { page_size: 20 } });
    const all = response.data.results || [];
    return [...all].sort(() => Math.random() - 0.5).slice(0, 5);
  },

  // Anuncios activos para el hero slider
  getAnnouncements: async (): Promise<any[]> => {
    const response = await api.get('/catalog/announcements');
    return Array.isArray(response.data) ? response.data : (response.data.results || []);
  },
};

// ── Demo mode switch ──────────────────────────────────────────────────────────
import { mockCatalogApi } from './mock/mockCatalog';
const isDemo = import.meta.env.VITE_DEMO_MODE === 'true';
export const catalogApi = isDemo ? mockCatalogApi : _realCatalogApi;
