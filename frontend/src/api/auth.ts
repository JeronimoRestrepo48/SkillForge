import api from './axios';
import { UserResponse, UserLoginPayload, UserRegisterPayload, TokenResponse } from '../types/auth';

const _realAuthApi = {
  // Registro de usuario (por defecto rol 'student' en backend)
  register: async (payload: UserRegisterPayload): Promise<UserResponse> => {
    const response = await api.post<UserResponse>('/auth/register', payload);
    return response.data;
  },

  // Login para obtener tokens
  login: async (payload: UserLoginPayload): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/token', payload);
    return response.data;
  },

  // Obtener perfil del usuario actual
  getMe: async (): Promise<UserResponse> => {
    const response = await api.get<UserResponse>('/auth/me');
    return response.data;
  },
  // Instructor Profiles
  getInstructorProfile: async (userId: number): Promise<any> => {
    const response = await api.get(`/auth/instructors/${userId}/profile`);
    return response.data;
  },
  updateInstructorProfile: async (userId: number, data: any): Promise<any> => {
    const response = await api.put(`/auth/instructors/${userId}/profile`, data);
    return response.data;
  },
};

// ── Demo mode switch ──────────────────────────────────────────────────────────
import { mockAuthApi } from './mock/mockAuth';
const isDemo = import.meta.env.VITE_DEMO_MODE === 'true';
export const authApi = isDemo ? mockAuthApi : _realAuthApi;
