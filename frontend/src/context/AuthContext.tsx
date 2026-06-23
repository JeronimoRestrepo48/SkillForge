import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { authApi } from '../api/auth';
import { UserResponse, UserLoginPayload, UserRegisterPayload } from '../types/auth';

// Demo mode: import demo user data
const isDemo = import.meta.env.VITE_DEMO_MODE === 'true';

interface AuthContextType {
  user: UserResponse | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (payload: UserLoginPayload) => Promise<void>;
  register: (payload: UserRegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadCurrentUser = async () => {
    // Demo mode: auto-login immediately
    if (isDemo) {
      const { DEMO_USER } = await import('../data/mockData');
      setUser(DEMO_USER);
      localStorage.setItem('access_token', 'demo_access_token_skillforge');
      localStorage.setItem('refresh_token', 'demo_refresh_token_skillforge');
      setLoading(false);
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (err) {
      console.error('Error cargando usuario inicial', err);
      // Limpieza segura en caso de token corrupto o expirado
      clearAuthData();
    } finally {
      setLoading(false);
    }
  };

  const clearAuthData = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  // Escuchar eventos globales de deslogueo automático (gatillados por interceptores Axios)
  useEffect(() => {
    const handleAuthLogout = () => {
      clearAuthData();
    };

    window.addEventListener('auth-logout', handleAuthLogout);
    loadCurrentUser();

    return () => {
      window.removeEventListener('auth-logout', handleAuthLogout);
    };
  }, []);

  const login = async (payload: UserLoginPayload) => {
    setLoading(true);
    setError(null);
    try {
      const tokens = await authApi.login(payload);
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Error en el inicio de sesión. Revisa tus credenciales.';
      setError(msg);
      clearAuthData();
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  };

  const register = async (payload: UserRegisterPayload) => {
    setLoading(true);
    setError(null);
    try {
      await authApi.register(payload);
      // Auto login tras registro exitoso
      await login({ username: payload.username, password: payload.password });
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Error en el registro. Intenta con otro usuario o email.';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    clearAuthData();
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};
