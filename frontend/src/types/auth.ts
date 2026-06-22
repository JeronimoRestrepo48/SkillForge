export interface UserResponse {
  id: number;
  username: string;
  email: string;
  role: 'student' | 'instructor' | 'admin';
  nombre_completo?: string | null;
  telefono?: string | null;
  ciudad?: string | null;
  pais?: string | null;
  created_at?: string | null;
}

export interface UserLoginPayload {
  username: string; // ¡Nota! El backend usa username y password para /token
  password: string;
}

export interface UserRegisterPayload {
  username: string;
  email: string;
  password: string;
  role?: 'student' | 'instructor';
  nombre_completo?: string;
  telefono?: string;
  ciudad?: string;
  pais?: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

export interface InstructorProfile {
  id: number;
  user_id: number;
  bio: string | null;
  carrera: string | null;
  estudios: string | null;
  linkedin_url: string | null;
  sitio_web: string | null;
  avatar_url: string | null;
}
