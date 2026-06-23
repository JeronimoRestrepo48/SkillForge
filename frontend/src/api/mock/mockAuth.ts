// Mock implementation of authApi for demo mode
import { DEMO_USER, DEMO_INSTRUCTOR_PROFILE } from '../../data/mockData';
import type { UserResponse, TokenResponse, UserRegisterPayload } from '../../types/auth';

const delay = (ms = 300) => new Promise(r => setTimeout(r, ms));

export const mockAuthApi = {
  register: async (_payload: UserRegisterPayload): Promise<UserResponse> => {
    await delay();
    return DEMO_USER;
  },

  login: async (_payload: any): Promise<TokenResponse> => {
    await delay(200);
    // Simulate token storage
    localStorage.setItem('access_token', 'demo_access_token_skillforge');
    localStorage.setItem('refresh_token', 'demo_refresh_token_skillforge');
    return {
      access: 'demo_access_token_skillforge',
      refresh: 'demo_refresh_token_skillforge',
    };
  },

  getMe: async (): Promise<UserResponse> => {
    await delay(100);
    return DEMO_USER;
  },

  getInstructorProfile: async (_userId: number): Promise<any> => {
    await delay(200);
    return DEMO_INSTRUCTOR_PROFILE;
  },

  updateInstructorProfile: async (_userId: number, data: any): Promise<any> => {
    await delay();
    return { ...DEMO_INSTRUCTOR_PROFILE, ...data };
  },
};
