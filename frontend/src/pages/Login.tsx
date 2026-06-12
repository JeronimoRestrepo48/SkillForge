import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Obtener la ruta de redirección si veníamos de una ProtectedRoute
  const from = (location.state as any)?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!username.trim() || !password.trim()) {
      setLocalError('Por favor, ingresa tu usuario y contraseña.');
      return;
    }

    try {
      await login({ username, password });
      navigate(from, { replace: true });
    } catch (err: any) {
      // El error ya es manejado por el contexto, pero podemos capturar fallas locales aquí
      console.error(err);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh] p-4">
      <div className="w-full max-w-md p-8 rounded-2xl glass-effect border border-zinc-800 shadow-2xl">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold tracking-tight">Iniciar Sesión</h2>
          <p className="text-sm text-text-secondary mt-2">
            Ingresa a tu cuenta de SkillForge para continuar aprendiendo
          </p>
        </div>

        {(error || localError) && (
          <div className="bg-red-900/30 border border-red-500/50 text-red-200 text-sm p-4 rounded-xl mb-6 flex items-start gap-2">
            <span className="font-semibold">⚠️ Error:</span>
            <span>{localError || error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-text-secondary mb-2">
              Nombre de usuario
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
              placeholder="Ej. jorge123"
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-text-secondary mb-2">
              Contraseña
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
              placeholder="••••••••"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl shadow-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                Verificando...
              </>
            ) : (
              'Ingresar'
            )}
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-text-secondary border-t border-zinc-850 pt-6">
          ¿No tienes una cuenta?{' '}
          <Link to="/register" className="text-primary-light hover:underline font-medium">
            Regístrate aquí
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
