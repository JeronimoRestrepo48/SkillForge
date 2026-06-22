import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { authApi } from '../api/auth';
import { useAuth } from '../context/AuthContext';
import { FadeInSection } from '../components/FadeInSection';

export const InstructorProfile: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const id = Number(userId);
  const { user } = useAuth();

  const { data: profile, isLoading, error } = useQuery({
    queryKey: ['instructorProfile', id],
    queryFn: () => authApi.getInstructorProfile(id),
    retry: false, // Don't retry on 404
  });

  const isOwnProfile = user?.id === id;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Si hay error (ej. 404), mostramos estado "No ha completado su perfil"
  if (error || !profile) {
    return (
      <div className="max-w-3xl mx-auto mt-12 p-8 text-center bg-[#111111] rounded-3xl border border-zinc-800 shadow-2xl glass-effect">
        <div className="w-24 h-24 mx-auto rounded-full bg-zinc-800 flex items-center justify-center text-4xl mb-4">
          👤
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Perfil de Instructor</h2>
        <p className="text-text-secondary">Este instructor aún no ha completado su perfil.</p>
        
        {isOwnProfile && (
          <Link to="/instructor/profile/edit" className="mt-6 inline-block px-6 py-3 bg-primary hover:bg-primary-dark text-white rounded-xl font-semibold transition">
            Crear mi perfil
          </Link>
        )}
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto mt-8 mb-16 space-y-8 px-4">
      <div className="bg-[#111111] rounded-3xl border border-zinc-800 shadow-2xl overflow-hidden glass-effect">
        <div className="h-32 bg-zinc-800/50 relative">
          {/* Cover background pattern */}
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary via-zinc-900 to-[#0A0A0A]"></div>
        </div>
        
        <div className="px-8 pb-8 relative">
          {/* Avatar */}
          <div className="absolute -top-16 left-8">
            {profile.avatar_url ? (
              <img src={profile.avatar_url} alt="Avatar" className="w-32 h-32 rounded-full border-4 border-[#111111] object-cover bg-zinc-800" />
            ) : (
              <div className="w-32 h-32 rounded-full border-4 border-[#111111] bg-zinc-800 flex items-center justify-center text-5xl">
                👤
              </div>
            )}
          </div>
          
          <div className="flex justify-end pt-4 h-16">
            {isOwnProfile && (
              <Link to="/instructor/profile/edit" className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-xl text-sm font-semibold transition border border-zinc-700">
                Editar mi perfil
              </Link>
            )}
          </div>

          <div className="mt-2 space-y-6">
            <div>
              <h1 className="text-3xl font-extrabold text-white">Instructor</h1>
              <p className="text-primary font-mono text-sm mt-1">{profile.carrera || 'Educador'}</p>
            </div>

            <FadeInSection delay={0}>
              <div className="prose prose-invert max-w-none">
                <h3 className="text-xl font-bold text-white mb-2">Sobre mí</h3>
                <p className="text-text-secondary leading-relaxed whitespace-pre-wrap">
                  {profile.bio || 'Sin biografía.'}
                </p>
              </div>
            </FadeInSection>

            {profile.estudios && (
              <FadeInSection delay={0.1}>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Formación y Estudios</h3>
                  <p className="text-text-secondary leading-relaxed whitespace-pre-wrap">
                    {profile.estudios}
                  </p>
                </div>
              </FadeInSection>
            )}

            <div className="flex gap-4 pt-4 border-t border-zinc-800/50">
              {profile.linkedin_url && (
                <a href={profile.linkedin_url} target="_blank" rel="noreferrer" className="text-primary hover:text-primary-light transition flex items-center gap-2">
                  <span>🔗</span> LinkedIn
                </a>
              )}
              {profile.sitio_web && (
                <a href={profile.sitio_web} target="_blank" rel="noreferrer" className="text-text-secondary hover:text-white transition flex items-center gap-2">
                  <span>🌐</span> Sitio Web
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InstructorProfile;
