import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { useCoursesQuery } from '../hooks/useCourses';
import { catalogApi } from '../api/catalog';
import { FadeInSection } from '../components/FadeInSection';
import { HeroSlider } from '../components/HeroSlider';

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
  const { t } = useTranslation();
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
      title: t('home.why_cert_title'),
      desc: t('home.why_cert_desc'),
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
      title: t('home.why_inst_title'),
      desc: t('home.why_inst_desc'),
    },
    {
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24"
          fill="none" stroke="#39FF14" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M3 17l6 -6l4 4l8 -9"/><path d="M14 15l7 -7"/>
        </svg>
      ),
      title: t('home.why_pace_title'),
      desc: t('home.why_pace_desc'),
    },
  ];

  return (
    <section className="w-full max-w-6xl mx-auto px-4 py-16">
      <h2 className="text-2xl md:text-3xl font-extrabold text-white mb-10 tracking-tight">
        {t('home.why_prefix')}<span style={{ color: '#39FF14' }}>SkillForge</span>
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
  const { t } = useTranslation();
  const { data: featuredData } = useCoursesQuery({ page_size: 3 });
  const featured = Array.isArray(featuredData?.results) ? featuredData!.results.slice(0, 3) : [];

  // Data for the hero slider
  const { data: sliderFeatured = [] } = useQuery({
    queryKey: ['sliderFeatured'],
    queryFn: () => catalogApi.getFeaturedCourses(),
    staleTime: 5 * 60 * 1000,
  });
  const { data: sliderRecent = [] } = useQuery({
    queryKey: ['sliderRecent'],
    queryFn: async () => {
      const res = await catalogApi.getCourses({ page_size: 4 });
      return [...(res.results || [])].sort((a, b) => b.id - a.id).slice(0, 4);
    },
    staleTime: 5 * 60 * 1000,
  });
  const { data: announcements = [] } = useQuery({
    queryKey: ['announcements'],
    queryFn: () => catalogApi.getAnnouncements(),
    staleTime: 5 * 60 * 1000,
  });

  return (
    <div className="flex flex-col w-full gap-12">

      {/* ── Hero Slider ──────────────────────────────────── */}
      <FadeInSection delay={0}>
        {(sliderFeatured.length > 0 || sliderRecent.length > 0 || announcements.length > 0) ? (
          <HeroSlider
            featuredCourses={sliderFeatured}
            recentCourses={sliderRecent}
            announcements={announcements}
          />
        ) : (
          <div className="rounded-3xl border border-zinc-800 bg-zinc-900 animate-pulse" style={{ minHeight: '520px' }} />
        )}
      </FadeInSection>

      {/* ── Cursos destacados ─────────────────────────────────────────── */}
      {featured.length > 0 && (
        <FadeInSection delay={0.1}>
        <section className="w-full max-w-6xl mx-auto px-4 py-14">
          <h2 className="text-2xl md:text-3xl font-extrabold text-white mb-8 tracking-tight">
            {t('home.featured')}
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
                        🕒 {course.duracion_horas || 0} {t('catalog.hours')}
                      </span>
                      <span className="font-mono font-bold text-xs" style={{ color: '#39FF14' }}>
                        {course.price === 0 ? t('catalog.free') : `$${Number(course.price).toLocaleString('es-CO')} COP`}
                      </span>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>
        </FadeInSection>
      )}

      {/* ── Por qué SkillForge ────────────────────────────────────────── */}
      <FadeInSection delay={0.2}>
        <WhySkillForge />
      </FadeInSection>
    </div>
  );
};

export default Home;
