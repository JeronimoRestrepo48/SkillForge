import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';
import { Trayectoria } from '../types/catalog';
import { CourseCard } from '../components/CourseCard';

export const TrayectoriaDetail: React.FC = () => {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const trayectoriaId = Number(id);

  const { data: trayectoria, isLoading, error } = useQuery<Trayectoria>({
    queryKey: ['trayectoria', trayectoriaId],
    queryFn: () => catalogApi.getTrayectoriaDetail(trayectoriaId),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
      </div>
    );
  }

  if (error || !trayectoria) {
    return (
      <div className="text-center p-8 mt-12 bg-red-950/20 border border-red-900/50 rounded-2xl text-red-200">
        {t('trayectorias.not_found')}
      </div>
    );
  }

  // Ordenar cursos por sort_order
  const sortedCursos = [...(trayectoria.cursos || [])].sort((a, b) => a.sort_order - b.sort_order);

  return (
    <div className="space-y-8 mt-4">
      {/* Header */}
      <div className="relative rounded-3xl overflow-hidden border border-zinc-800 shadow-2xl bg-zinc-900 p-8 md:p-12">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-zinc-900 to-[#0A0A0A]"></div>
        <div className="relative z-10 max-w-3xl space-y-4">
          <Link to="/trayectorias" className="text-primary hover:text-primary-light text-sm font-semibold mb-4 inline-block">
            {t('trayectorias.back')}
          </Link>
          {trayectoria.categoria_general && (
            <span className="text-xs font-mono text-primary-light bg-primary/10 px-3 py-1 rounded-full border border-primary/20 block w-max">
              {trayectoria.categoria_general}
            </span>
          )}
          <h1 className="text-3xl md:text-5xl font-extrabold text-white">{trayectoria.nombre}</h1>
          <p className="text-text-secondary text-lg leading-relaxed">
            {trayectoria.descripcion || t('trayectorias.default_desc')}
          </p>
        </div>
      </div>

      {/* Lista de Cursos */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-white">{t('trayectorias.courses_in_path')}</h2>
        
        {sortedCursos.length === 0 ? (
          <p className="text-text-muted italic">{t('trayectorias.no_courses_assigned')}</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedCursos.map((tc, idx) => (
              <div key={tc.course_id} className="relative">
                <div className="absolute -left-3 -top-3 w-8 h-8 bg-zinc-800 text-white font-mono text-xs rounded-full flex items-center justify-center border-2 border-primary z-10 shadow-lg">
                  {idx + 1}
                </div>
                {tc.course && <CourseCard course={tc.course} />}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TrayectoriaDetail;
