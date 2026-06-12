import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCoursesQuery } from '../hooks/useCourses';

// ── Utilidad compartida de imagen por categoría ──────────────────────────────
export const getCategoryImage = (categoryName?: string): string => {
  const name = (categoryName || '').toLowerCase();
  if (/programaci|frontend|backend|código|code|software|web dev/.test(name))
    return 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=1200&q=80';
  if (/dise|ux|ui/.test(name))
    return 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=1200&q=80';
  if (/data|ia|inteligencia|machine|ml/.test(name))
    return 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80';
  if (/marketing/.test(name))
    return 'https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a?w=1200&q=80';
  if (/finanz|negocio|business/.test(name))
    return 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80';
  return 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1200&q=80';
};

// ── Sección "Por qué SkillForge" ─────────────────────────────────────────────
const WhySkillForge: React.FC = () => {
  const features = [
    {
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24"
          fill="none" stroke="#39FF14" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M15 15m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0"/>
          <path d="M13 17.5v4.5l2 -1.5l2 1.5v-4.5"/>
          <path d="M10 19h-5a2 2 0 0 1 -2 -2v-10c0 -1.1 .9 -2 2 -2h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -2 2h-1"/>
          <path d="M6 9l12 0"/><path d="M6 12l3 0"/>
        </svg>
      ),
      title: 'Certificados reconocidos',
      desc: 'Obtén certificados verificables que puedes compartir en LinkedIn y tu CV',
    },
    {
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24"
          fill="none" stroke="#39FF14" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M9 7m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0"/>
          <path d="M3 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          <path d="M21 21v-2a4 4 0 0 0 -3 -3.85"/>
        </svg>
      ),
      title: 'Instructores expertos',
      desc: 'Aprende de profesionales activos en la industria con experiencia real',
    },
    {
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24"
          fill="none" stroke="#39FF14" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M3 17l6 -6l4 4l8 -9"/><path d="M14 15l7 -7"/>
        </svg>
      ),
      title: 'Aprende a tu ritmo',
      desc: 'Acceso de por vida al contenido y actualizaciones futuras del curso',
    },
  ];

  return (
    <section className="w-full max-w-6xl mx-auto px-4 py-16">
      <h2 className="text-2xl md:text-3xl font-extrabold text-white mb-10 tracking-tight">
        Por qué <span style={{ color: '#39FF14' }}>SkillForge</span>
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((f) => (
          <div
            key={f.title}
            style={{ background: '#111111', border: '1px solid #1e1e1e' }}
            className="rounded-2xl p-7 flex flex-col gap-4 hover:border-accent/40 transition-colors duration-200"
          >
            <div>{f.icon}</div>
            <h3 className="text-white font-bold text-base">{f.title}</h3>
            <p className="text-sm" style={{ color: '#9CA3AF' }}>{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

// ── Componente principal Home ─────────────────────────────────────────────────
export const Home: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const { data: featuredData } = useCoursesQuery({ page_size: 3 });
  const featured = Array.isArray(featuredData?.results) ? featuredData!.results.slice(0, 3) : [];

  return (
    <div className="flex flex-col w-full">

      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <div style={{ position: 'relative', height: '480px', overflow: 'hidden', width: '100%' }}>
        {/* Imagen de fondo */}
        <div
          style={{
            position: 'absolute', inset: 0,
            backgroundImage: "url('https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1200&q=80')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />
        {/* Overlay oscuro */}
        <div
          style={{
            position: 'absolute', inset: 0,
            background: 'linear-gradient(to bottom, rgba(10,10,10,0.72) 0%, rgba(10,10,10,0.94) 100%)',
          }}
        />
        {/* Contenido */}
        <div
          style={{ position: 'relative', zIndex: 1 }}
          className="flex flex-col items-center justify-center h-full text-center px-6"
        >
          {isAuthenticated && user ? (
            <>
              <span
                className="text-xs font-mono font-bold uppercase tracking-widest px-4 py-1.5 rounded-full mb-6 border"
                style={{ color: '#39FF14', background: 'rgba(57,255,20,0.08)', borderColor: 'rgba(57,255,20,0.27)' }}
              >
                Plataforma colombiana de aprendizaje
              </span>
              <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white mb-4">
                Bienvenido de nuevo,{' '}
                <span style={{ color: '#39FF14' }}>{user.username}</span>
              </h1>
              <p className="text-lg text-gray-300 max-w-xl mb-8">
                Continúa donde lo dejaste o explora nuevos cursos.
              </p>
              <div className="flex flex-wrap gap-4 justify-center">
                <Link
                  to="/dashboard"
                  style={{ background: '#39FF14', color: '#0a0a0a' }}
                  className="px-7 py-3 font-bold rounded-xl shadow-lg transition hover:opacity-90"
                >
                  Mis cursos
                </Link>
                <Link
                  to="/courses"
                  className="px-7 py-3 bg-zinc-800 hover:bg-zinc-700 text-white font-semibold rounded-xl transition"
                >
                  Explorar catálogo
                </Link>
              </div>
            </>
          ) : (
            <>
              <span
                className="text-xs font-mono font-bold uppercase tracking-widest px-4 py-1.5 rounded-full mb-6 border"
                style={{ color: '#39FF14', background: 'rgba(57,255,20,0.08)', borderColor: 'rgba(57,255,20,0.27)' }}
              >
                Plataforma colombiana de aprendizaje
              </span>
              <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white mb-4 leading-tight">
                Aprende habilidades que el{' '}
                <br className="hidden md:block" />
                mercado{' '}
                <span style={{ color: '#39FF14' }}>demanda hoy</span>
              </h1>
              <p className="text-lg text-gray-300 max-w-2xl mb-8">
                Miles de cursos en tecnología, diseño y negocios. Certificados reconocidos por empresas líderes.
              </p>
              <div className="flex flex-wrap gap-4 justify-center">
                <Link
                  to="/courses"
                  style={{ background: '#39FF14', color: '#0a0a0a' }}
                  className="px-7 py-3 font-bold rounded-xl shadow-lg transition hover:opacity-90"
                >
                  Explorar cursos
                </Link>
                <Link
                  to="/register"
                  className="px-7 py-3 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl border border-white/20 transition backdrop-blur-sm"
                >
                  Ver planes
                </Link>
              </div>
            </>
          )}
        </div>
      </div>

      {/* ── Cursos destacados ─────────────────────────────────────────── */}
      {featured.length > 0 && (
        <section className="w-full max-w-6xl mx-auto px-4 py-14">
          <h2 className="text-2xl md:text-3xl font-extrabold text-white mb-8 tracking-tight">
            Cursos destacados
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {featured.map((course) => {
              const c = course as any;
              const categoryName = typeof c.categoria === 'object'
                ? (c.categoria?.name || '')
                : (c.category_name || '');
              const img = getCategoryImage(categoryName || course.title);
              return (
                <Link
                  to={`/courses/${course.id}`}
                  key={course.id}
                  style={{ background: '#111111', border: '1px solid #1e1e1e' }}
                  className="rounded-2xl overflow-hidden flex flex-col group hover:border-accent/40 transition-colors duration-200 shadow-lg"
                >
                  {/* Thumbnail */}
                  <div style={{ position: 'relative', height: '160px', overflow: 'hidden' }}>
                    <img
                      src={img}
                      alt={course.title}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      loading="lazy"
                    />
                    {/* Overlay inferior */}
                    <div style={{
                      position: 'absolute', inset: 0,
                      background: 'linear-gradient(to bottom, transparent 40%, rgba(17,17,17,0.85) 100%)',
                    }} />
                    {/* Badge categoría */}
                    <span
                      style={{
                        position: 'absolute', top: 8, left: 8,
                        background: '#39FF14', color: '#0a0a0a',
                        fontSize: '10px', fontWeight: 700,
                        padding: '2px 8px', borderRadius: '9999px',
                        textTransform: 'uppercase', letterSpacing: '0.05em',
                      }}
                    >
                      {categoryName || course.nivel_dificultad || 'Curso'}
                    </span>
                  </div>
                  {/* Info */}
                  <div className="p-5 flex flex-col gap-2 flex-grow">
                    <h3 className="text-white font-bold text-sm leading-snug group-hover:text-accent transition-colors">
                      {course.title}
                    </h3>
                    <p className="text-xs line-clamp-2" style={{ color: '#9CA3AF' }}>
                      {course.description}
                    </p>
                    <div className="mt-auto pt-3 flex justify-between items-center border-t" style={{ borderColor: '#1e1e1e' }}>
                      <span className="text-xs" style={{ color: '#9CA3AF' }}>
                        🕒 {course.duracion_horas || 0} horas
                      </span>
                      <span className="font-mono font-bold text-xs" style={{ color: '#39FF14' }}>
                        {course.price === 0 ? 'Gratis' : `$${Number(course.price).toLocaleString('es-CO')} COP`}
                      </span>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>
      )}

      {/* ── Por qué SkillForge ────────────────────────────────────────── */}
      <WhySkillForge />
    </div>
  );
};

export default Home;
