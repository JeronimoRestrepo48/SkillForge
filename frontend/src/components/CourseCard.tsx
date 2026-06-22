import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Course } from '../types/catalog';
import { getCategoryImage } from '../pages/Home';

interface CourseCardProps {
  course: Course;
}

export const CourseCard: React.FC<CourseCardProps> = ({ course }) => {
  const { t } = useTranslation();
  // Extraer nombre de categoría si viene como objeto anidado
  const categoryName = typeof (course as any).categoria === 'object'
    ? ((course as any).categoria?.name || '')
    : '';

  // Imagen: thumbnail propio → Unsplash por categoría
  const thumbnail = (course as any).thumbnail as string | undefined;
  const imgSrc = thumbnail || getCategoryImage(categoryName || course.title);

  return (
    <motion.div
      whileHover={{ y: -6, boxShadow: '0 0 24px rgba(57,255,20,0.15)' }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      style={{ background: '#111111', border: '1px solid #1e1e1e' }}
      className="rounded-2xl overflow-hidden flex flex-col h-full shadow-lg group hover:border-accent/40 transition-colors duration-200"
    >
      {/* ── Imagen ──────────────────────────────────────────────────── */}
      <div style={{ position: 'relative', height: '110px', overflow: 'hidden' }}>
        <img
          src={imgSrc}
          alt={course.title}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          loading="lazy"
        />
        {/* Gradient overlay inferior */}
        <div
          style={{
            position: 'absolute', inset: 0,
            background: 'linear-gradient(to bottom, transparent 30%, rgba(17,17,17,0.82) 100%)',
          }}
        />
        {/* Badge de categoría */}
        <span
          style={{
            position: 'absolute', top: 8, left: 8,
            background: '#39FF14', color: '#0a0a0a',
            fontSize: '10px', fontWeight: 700,
            padding: '2px 8px', borderRadius: '9999px',
            textTransform: 'uppercase', letterSpacing: '0.05em',
            whiteSpace: 'nowrap', maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis',
          }}
        >
          {categoryName || (course.nivel_dificultad ? t(`common.difficulty.${course.nivel_dificultad}`, course.nivel_dificultad) : t('catalog.title'))}
        </span>
      </div>

      {/* ── Cuerpo ──────────────────────────────────────────────────── */}
      <div className="p-5 flex flex-col flex-grow">
        <h3 className="text-white font-bold text-sm leading-snug mb-2 group-hover:text-accent transition-colors line-clamp-2">
          {course.title}
        </h3>
        <p className="text-xs line-clamp-2 mb-4 flex-grow" style={{ color: '#9CA3AF' }}>
          {course.description || 'Sin descripción disponible para este curso.'}
        </p>

        {/* Metadatos y Precio */}
        <div
          className="flex justify-between items-center text-xs mb-4 pt-3 border-t"
          style={{ borderColor: '#1e1e1e', color: '#9CA3AF' }}
        >
          <span>🕒 {course.duracion_horas || 0} {t('catalog.hours')}</span>
          <span className="font-mono font-bold" style={{ color: '#39FF14' }}>
            {course.price === 0 ? t('catalog.free') : `$${Number(course.price).toLocaleString('es-CO')} COP`}
          </span>
        </div>

        {/* Botón */}
        <Link
          to={`/courses/${course.id}`}
          style={{ background: '#1a1a1a', border: '1px solid #1e1e1e' }}
          className="w-full text-center py-2.5 text-white text-xs font-semibold rounded-xl transition duration-200 hover:bg-accent hover:text-black hover:border-accent"
        >
          {t('catalog.view_course')}
        </Link>
      </div>
    </motion.div>
  );
};

export default CourseCard;
