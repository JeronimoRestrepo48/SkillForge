import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import { LanguageSwitcher } from './LanguageSwitcher';

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const { t } = useTranslation();

  return (
    <nav className="glass-effect border-b border-zinc-800/80 sticky top-0 z-50 px-6 py-4 flex justify-between items-center transition shadow-lg">
      <div className="flex items-center gap-8">
        <Link to="/" className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
          <span className="text-primary">Skill</span>Forge
        </Link>
        <div className="hidden md:flex items-center gap-6 text-sm font-medium">
          <Link to="/courses" className="text-text-secondary hover:text-white transition">
            {t('nav.catalog')}
          </Link>
          <Link to="/trayectorias" className="text-text-secondary hover:text-white transition">
            {t('nav.routes')}
          </Link>
          {isAuthenticated && (
            <Link to="/dashboard" className="text-text-secondary hover:text-white transition">
              {t('nav.myLearning')}
            </Link>
          )}
          {isAuthenticated && (user?.role === 'instructor' || user?.role === 'admin') && (
            <Link to="/instructor" className="text-text-secondary hover:text-white transition">
              {t('nav.instructor')}
            </Link>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4">
        <LanguageSwitcher />
        
        {/* Carrito de compras */}
        <Link to="/cart" className="relative p-2 text-text-secondary hover:text-white transition" aria-label="Carrito">
          🛒
        </Link>

        {isAuthenticated && user ? (
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex flex-col text-right">
              <span className="text-sm font-semibold text-white">{user.username}</span>
              <div className="flex items-center justify-end gap-2 text-xs text-text-muted">
                <span className="capitalize">{user.role}</span>
                {(user.role === 'instructor' || user.role === 'admin') && (
                  <>
                    <span>•</span>
                    <Link to={`/instructors/${user.id}`} className="hover:text-white hover:underline transition">
                      {t('nav.myProfile')}
                    </Link>
                  </>
                )}
              </div>
            </div>
            <button
              onClick={logout}
              className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white text-sm font-semibold rounded-xl transition"
            >
              {t('nav.logout')}
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link
              to="/login"
              className="px-4 py-2 text-sm text-text-secondary hover:text-white font-semibold transition"
            >
              {t('nav.login')}
            </Link>
            <Link
              to="/register"
              className="px-4 py-2 bg-primary hover:bg-primary-dark text-white text-sm font-semibold rounded-xl transition shadow-md"
            >
              {t('nav.register')}
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
