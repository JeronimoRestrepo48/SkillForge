import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { AnimatePresence, motion } from 'framer-motion';
import { Course } from '../types/catalog';
import { getCategoryImage } from '../pages/Home';

// ── Types ─────────────────────────────────────────────────────────────────────

type SlideType = 'featured' | 'recent' | 'announcement';

interface Slide {
  type: SlideType;
  id: number;
  title: string;
  description?: string;
  badge: string;
  badgeColor: string;
  imagen_url?: string;
  courseId?: number;
  price?: number;
  nivel?: string;
}

interface HeroSliderProps {
  featuredCourses: Course[];
  recentCourses: Course[];
  announcements: any[];
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function courseToSlide(course: Course, type: SlideType, t: any): Slide {
  const cat = typeof (course as any).categoria === 'object'
    ? ((course as any).categoria?.name || '')
    : '';
  return {
    type,
    id: course.id,
    title: course.title,
    description: course.description || undefined,
    badge: type === 'recent' ? t('home.badge_new') : t('home.badge_featured'),
    badgeColor: type === 'recent' ? '#7C3AED' : '#39FF14',
    imagen_url: (course as any).thumbnail || getCategoryImage(cat || course.title),
    courseId: course.id,
    price: course.price,
    nivel: course.nivel_dificultad,
  };
}

// ── Arrow Buttons ─────────────────────────────────────────────────────────────

const ArrowBtn: React.FC<{ dir: 'left' | 'right'; onClick: () => void }> = ({ dir, onClick }) => (
  <button
    onClick={onClick}
    aria-label={dir === 'left' ? 'Slide anterior' : 'Slide siguiente'}
    className="absolute top-1/2 -translate-y-1/2 z-20 flex items-center justify-center w-11 h-11 rounded-full border border-white/20 bg-black/40 hover:bg-black/70 text-white backdrop-blur-sm transition"
    style={{ [dir === 'left' ? 'left' : 'right']: '1.25rem' }}
  >
    {dir === 'left' ? (
      <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
      </svg>
    ) : (
      <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
      </svg>
    )}
  </button>
);

// ── Main Component ────────────────────────────────────────────────────────────

export const HeroSlider: React.FC<HeroSliderProps> = ({
  featuredCourses,
  recentCourses,
  announcements,
}) => {
  const { t } = useTranslation();

  // Build slide list: up to 2 featured + up to 2 recent + all announcements
  const slides: Slide[] = [
    ...featuredCourses.slice(0, 2).map(c => courseToSlide(c, 'featured', t)),
    ...recentCourses.slice(0, 2).map(c => courseToSlide(c, 'recent', t)),
    ...announcements.slice(0, 3).map(a => ({
      type: 'announcement' as SlideType,
      id: a.id,
      title: a.titulo,
      description: a.descripcion,
      badge: t('home.announcement_badge'),
      badgeColor: '#F59E0B',
      imagen_url: a.imagen_url,
    })),
  ];

  const total = slides.length;
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [direction, setDirection] = useState<1 | -1>(1);

  const goTo = useCallback((idx: number, dir: 1 | -1 = 1) => {
    setDirection(dir);
    setCurrentIndex((idx + total) % total);
  }, [total]);

  const next = useCallback(() => goTo(currentIndex + 1, 1), [currentIndex, goTo]);
  const prev = useCallback(() => goTo(currentIndex - 1, -1), [currentIndex, goTo]);

  // Auto-play every 5s, paused on hover
  useEffect(() => {
    if (isPaused || total === 0) return;
    const timer = setInterval(next, 5000);
    return () => clearInterval(timer);
  }, [isPaused, next, total]);

  if (total === 0) return null;

  const slide = slides[currentIndex];

  const variants = {
    enter: (dir: number) => ({ opacity: 0, x: dir > 0 ? 80 : -80 }),
    center: { opacity: 1, x: 0 },
    exit: (dir: number) => ({ opacity: 0, x: dir > 0 ? -80 : 80 }),
  };

  return (
    <div
      className="relative w-full overflow-hidden rounded-3xl border border-zinc-800 shadow-2xl"
      style={{ minHeight: '520px' }}
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* ── Slide content ── */}
      <AnimatePresence custom={direction} mode="wait">
        <motion.div
          key={`${slide.type}-${slide.id}`}
          custom={direction}
          variants={variants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{ duration: 0.4, ease: 'easeInOut' }}
          className="absolute inset-0"
        >
          {/* Background image */}
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: slide.imagen_url ? `url('${slide.imagen_url}')` : undefined,
              backgroundColor: slide.imagen_url ? undefined : '#0a0a0a',
              backgroundSize: 'cover',
              backgroundPosition: 'center',
            }}
          />
          {/* Dark overlay */}
          <div
            className="absolute inset-0"
            style={{
              background:
                'linear-gradient(135deg, rgba(10,10,10,0.90) 0%, rgba(10,10,10,0.70) 55%, rgba(10,10,10,0.88) 100%)',
            }}
          />
          {/* Left green accent bar */}
          <div
            className="absolute left-0 top-0 bottom-0"
            style={{ width: '3px', background: '#39FF14' }}
          />

          {/* Slide body */}
          <div className="relative z-10 flex flex-col justify-end h-full px-10 py-12 md:px-16 md:py-14">
            {/* Badge */}
            <span
              className="inline-block self-start mb-4 px-3 py-1 text-xs font-bold font-mono uppercase tracking-widest rounded-full border"
              style={{
                color: slide.badgeColor,
                borderColor: `${slide.badgeColor}55`,
                background: `${slide.badgeColor}18`,
              }}
            >
              {slide.badge}
            </span>

            {/* Title */}
            <h2 className="text-3xl md:text-5xl font-extrabold text-white tracking-tight leading-tight max-w-2xl mb-3">
              {slide.title}
            </h2>

            {/* Description */}
            {slide.description && (
              <p className="text-text-secondary text-base md:text-lg leading-relaxed max-w-xl mb-6 line-clamp-2">
                {slide.description}
              </p>
            )}

            {/* Meta + CTA */}
            <div className="flex flex-wrap items-center gap-4">
              {slide.nivel && (
                <span className="text-xs font-mono text-primary-light bg-primary/10 border border-primary/20 px-3 py-1 rounded-full">
                  {slide.nivel}
                </span>
              )}
              {slide.price !== undefined && (
                <span className="text-2xl font-mono font-extrabold" style={{ color: '#39FF14' }}>
                  {slide.price === 0 ? t('home.free') : `$${Number(slide.price).toLocaleString('es-CO')} COP`}
                </span>
              )}
              {slide.courseId && (
                <motion.div whileTap={{ scale: 0.96 }} transition={{ type: 'spring', stiffness: 400, damping: 25 }}>
                  <Link
                    to={`/courses/${slide.courseId}`}
                    className="inline-block px-7 py-3 font-bold rounded-xl shadow-lg transition hover:opacity-90"
                    style={{ background: '#39FF14', color: '#0a0a0a' }}
                  >
                    {t('home.view_course')}
                  </Link>
                </motion.div>
              )}
              {slide.type === 'announcement' && !slide.courseId && (
                <Link
                  to="/courses"
                  className="inline-block px-7 py-3 font-semibold rounded-xl border border-white/20 bg-white/10 hover:bg-white/20 text-white transition backdrop-blur-sm"
                >
                  {t('home.explore_courses')}
                </Link>
              )}
            </div>
          </div>
        </motion.div>
      </AnimatePresence>

      {/* ── Arrows ── */}
      {total > 1 && (
        <>
          <ArrowBtn dir="left" onClick={prev} />
          <ArrowBtn dir="right" onClick={next} />
        </>
      )}

      {/* ── Dots ── */}
      {total > 1 && (
        <div className="absolute bottom-5 left-1/2 -translate-x-1/2 z-20 flex gap-2">
          {slides.map((_, i) => (
            <button
              key={i}
              onClick={() => goTo(i, i > currentIndex ? 1 : -1)}
              aria-label={`Ir al slide ${i + 1}`}
              className="rounded-full transition-all duration-300"
              style={{
                width: i === currentIndex ? '28px' : '8px',
                height: '8px',
                background: i === currentIndex ? '#39FF14' : 'rgba(255,255,255,0.35)',
              }}
            />
          ))}
        </div>
      )}

      {/* ── Progress bar ── */}
      {!isPaused && (
        <motion.div
          key={`progress-${currentIndex}`}
          className="absolute bottom-0 left-0 h-0.5 z-20"
          style={{ background: '#39FF14' }}
          initial={{ width: '0%' }}
          animate={{ width: '100%' }}
          transition={{ duration: 5, ease: 'linear' }}
        />
      )}
    </div>
  );
};

export default HeroSlider;
