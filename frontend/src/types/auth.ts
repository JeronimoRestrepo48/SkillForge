export interface UserResponse {
  id: number;
  username: string;
  email: string;
  role: 'student' | 'instructor' | 'admin';
}

export interface UserLoginPayload {
  username: string; // ¡Nota! El backend usa username y password para /token
  password: string;
}

export interface UserRegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}
