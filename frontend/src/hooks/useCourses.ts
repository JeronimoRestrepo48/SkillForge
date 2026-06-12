import { useQuery } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';

export const useCoursesQuery = (params?: { q?: string; categoria?: number; page?: number; page_size?: number }) => {
  return useQuery({
    queryKey: ['courses', params],
    queryFn: () => catalogApi.getCourses(params),
    placeholderData: (previousData) => previousData, // Evita parpadeos en búsquedas con debounce
  });
};

export const useCourseDetailQuery = (courseId: number) => {
  return useQuery({
    queryKey: ['courseDetail', courseId],
    queryFn: () => catalogApi.getCourseDetail(courseId),
    enabled: !!courseId,
  });
};

export const useCategoriesQuery = (params?: { page?: number; page_size?: number }) => {
  return useQuery({
    queryKey: ['categories', params],
    queryFn: () => catalogApi.getCategories(params),
    staleTime: 60 * 60 * 1000, // Las categorías cambian poco, se guardan en caché por 1 hora
  });
};

export const useCourseProgressQuery = (courseId: number, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['courseProgress', courseId],
    queryFn: () => catalogApi.getCourseProgress(courseId),
    enabled: enabled && !!courseId,
  });
};
