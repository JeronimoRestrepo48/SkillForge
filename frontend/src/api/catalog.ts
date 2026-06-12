import api from './axios';
import { 
  Course, 
  CourseDetail, 
  Category, 
  PaginatedResponse, 
  LessonProgress, 
  CourseProgress 
} from '../types/catalog';

export const catalogApi = {
  // Listar cursos con búsqueda opcional, filtrado y paginación
  getCourses: async (params?: { q?: string; categoria?: number; page?: number; page_size?: number }): Promise<PaginatedResponse<Course>> => {
    const response = await api.get<PaginatedResponse<Course>>('/catalog/courses', { params });
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
};
