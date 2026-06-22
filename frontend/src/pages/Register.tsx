import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { COUNTRIES_SORTED } from '../data/countries';
import { User, Mail, Lock, MapPin, Briefcase, GraduationCap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';

export const Register: React.FC = () => {
  const { t } = useTranslation();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState<'student' | 'instructor'>('student');
  const [nombreCompleto, setNombreCompleto] = useState('');
  const [selectedCountry, setSelectedCountry] = useState(
    COUNTRIES_SORTED.find(c => c.iso === 'CO')! // Colombia por defecto
  );
  const [dialCode, setDialCode] = useState('+57');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [ciudad, setCiudad] = useState('');

  const [localError, setLocalError] = useState<string | null>(null);
  const { register, loading, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!username.trim() || !email.trim() || !password.trim() || !nombreCompleto.trim()) {
      setLocalError('Por favor, completa los campos obligatorios (*).');
      return;
    }

    if (password !== confirmPassword) {
      setLocalError('Las contraseñas no coinciden.');
      return;
    }

    try {
      const telefonoCompleto = phoneNumber ? `${dialCode}${phoneNumber}` : undefined;
      await register({
        username,
        email,
        password,
        role,
        nombre_completo: nombreCompleto,
        telefono: telefonoCompleto,
        ciudad,
        pais: selectedCountry.name
      });
      // The context will automatically log the user in, then we navigate depending on role
      navigate(role === 'instructor' ? '/instructor' : '/dashboard');
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh] py-12 px-4 sm:px-6 lg:px-8">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-2xl p-8 rounded-2xl glass-effect border border-zinc-800 shadow-2xl"
      >
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold tracking-tight">{t('register.title')}</h2>
          <p className="text-sm text-text-secondary mt-2">
            {t('register.subtitle')}
          </p>
        </div>

        <AnimatePresence>
          {(error || localError) && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-red-900/30 border border-red-500/50 text-red-200 text-sm p-4 rounded-xl mb-6 flex items-start gap-2"
            >
              <span className="font-semibold">⚠️</span>
              <span>{localError || error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* Role Selector */}
          <div className="flex gap-4 p-1 bg-background-deep rounded-xl border border-zinc-800">
            <button
              type="button"
              onClick={() => setRole('student')}
              className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg font-medium transition-all ${
                role === 'student' 
                  ? 'bg-primary text-white shadow-md' 
                  : 'text-text-secondary hover:text-text-primary hover:bg-zinc-800/50'
              }`}
            >
              <GraduationCap size={20} />
              {t('register.student_title')}
            </button>
            <button
              type="button"
              onClick={() => setRole('instructor')}
              className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg font-medium transition-all ${
                role === 'instructor' 
                  ? 'bg-primary text-white shadow-md' 
                  : 'text-text-secondary hover:text-text-primary hover:bg-zinc-800/50'
              }`}
            >
              <Briefcase size={20} />
              {t('register.instructor_title')}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">{t('register.username')} *</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
                  placeholder="ej. carlos_dev"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">{t('register.email')} *</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
                  placeholder="correo@ejemplo.com"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Nombre Completo */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-text-secondary mb-1">{t('register.full_name')} *</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
                <input
                  type="text"
                  value={nombreCompleto}
                  onChange={(e) => setNombreCompleto(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
                  placeholder="Carlos López"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">{t('register.password')} *</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
                  placeholder="••••••••"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">{t('register.confirm_password')} *</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
                  placeholder="••••••••"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Telefono */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                {t('register.phone')} <span className="text-text-muted">{t('register.phone_optional')}</span>
              </label>
              <div className="flex gap-2">
                {/* Código de país — readonly, se actualiza al cambiar país */}
                <div className="flex items-center gap-1.5 px-3 py-2.5 bg-zinc-900 border border-zinc-800 rounded-xl text-sm text-text-secondary font-mono min-w-[80px] select-none">
                  <span>{selectedCountry.flag}</span>
                  <span>{dialCode}</span>
                </div>
                {/* Número */}
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ''))}
                  placeholder="3001234567"
                  className="flex-1 px-4 py-2.5 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Pais & Ciudad */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">{t('register.country')}</label>
                <select
                  value={selectedCountry.iso}
                  onChange={(e) => {
                    const country = COUNTRIES_SORTED.find(c => c.iso === e.target.value)!;
                    setSelectedCountry(country);
                    // Sincronizar el dialCode con el campo de teléfono
                    setDialCode(country.dialCode);
                  }}
                  className="w-full px-4 py-2.5 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition appearance-none"
                  disabled={loading}
                >
                  {COUNTRIES_SORTED.map(country => (
                    <option key={country.iso} value={country.iso}>
                      {country.flag} {country.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">{t('register.city')}</label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
                  <input
                    type="text"
                    value={ciudad}
                    onChange={(e) => setCiudad(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 bg-background-deep border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary transition"
                    placeholder="Ciudad"
                    disabled={loading}
                  />
                </div>
              </div>
            </div>

          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 mt-4 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl shadow-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                {t('register.creating')}
              </>
            ) : (
              t('register.submit')
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-text-secondary border-t border-zinc-850 pt-6">
          {t('register.already_have')}{' '}
          <Link to="/login" className="text-primary-light hover:underline font-medium">
            {t('register.login_here')}
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default Register;
