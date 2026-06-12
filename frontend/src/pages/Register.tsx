import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Register: React.FC = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);
  const { register, loading, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!username.trim() || !email.trim() || !password.trim()) {
      setLocalError('Por favor, completa todos los campos.');
      return;
    }

    if (password !== confirmPassword) {
      setLocalError('Las contraseñas no coinciden.');
      return;
    }

    try {
      await register({ username, email, password });
      navigate('/dashboard');
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh] p-4">
      <div className="w-full max-w-md p-8 rounded-2xl glass-effect border border-zinc-800 shadow-2xl">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold tracking-tight">Crea tu Cuenta</h2>
          <p className="text-sm text-text-secondary mt-2">
            Únete hoy a SkillForge y potencia tu crecimiento profesional
          </p>
        </div>

        {(error || localError) && (
          <div className="bg-red-900/30 border border-red-500/50 text-red-200 text-sm p-4 rounded-xl mb-6 flex items-start gap-2">
            <span className="font-semibold">⚠️ Error:</span>
            <span>{localError || error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-text-secondary mb-1">
              Nombre de usuario
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
              placeholder="Ej. jorge_dev"
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-text-secondary mb-1">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
              placeholder="correo@ejemplo.com"
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-text-secondary mb-1">
              Contraseña
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
              placeholder="••••••••"
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-text-secondary mb-1">
              Confirmar Contraseña
            </label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-4 py-2 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
              placeholder="••••••••"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 mt-4 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl shadow-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                Creando cuenta...
              </>
            ) : (
              'Registrarse'
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-text-secondary border-t border-zinc-850 pt-6">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-primary-light hover:underline font-medium">
            Inicia sesión aquí
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
