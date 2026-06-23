import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

// Base URL dinámica: usa VITE_API_URL en producción (ej. EC2) o '/api' en local (Docker/Nginx)
const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (token) {
      prom.resolve(token);
    } else {
      prom.reject(error);
    }
  });
  failedQueue = [];
};

// 1. Interceptor de Request: Adjuntar JWT Access Token si existe
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 2. Interceptor de Response: Manejo de errores y refresco automático de token (401)
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Si el error no es 401 o la petición ya fue reintentada, rechazar directamente
    if (error.response?.status !== 401 || !originalRequest || originalRequest._retry) {
      return Promise.reject(error);
    }

    // Evitar bucle infinito si falla el propio endpoint de refresh o login
    if (originalRequest.url?.includes('/auth/token') && !originalRequest.url?.includes('/auth/token/refresh')) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((token) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          return api(originalRequest);
        })
        .catch((err) => {
          return Promise.reject(err);
        });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) {
      isRefreshing = false;
      logoutAndRedirect();
      return Promise.reject(error);
    }

    try {
      // Intentamos refrescar el access token usando el refresh token
      const response = await axios.post<{ access: string }>(`${API_BASE}/auth/token/refresh`, {
        refresh: refreshToken,
      });

      const newAccessToken = response.data.access;
      localStorage.setItem('access_token', newAccessToken);

      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      }

      processQueue(null, newAccessToken);
      isRefreshing = false;

      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      isRefreshing = false;
      logoutAndRedirect();
      return Promise.reject(refreshError);
    }
  }
);

function logoutAndRedirect() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  // Dispatch custom event to notify components/Context
  window.dispatchEvent(new Event('auth-logout'));
  if (window.location.pathname !== '/login') {
    window.location.href = '/login';
  }
}

export default api;
