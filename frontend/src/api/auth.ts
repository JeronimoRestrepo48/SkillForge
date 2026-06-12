import api from './axios';
import { UserResponse, UserLoginPayload, UserRegisterPayload, TokenResponse } from '../types/auth';

export const authApi = {
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
};
