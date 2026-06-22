import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { transactionsApi } from '../api/transactions';
import { certificatesApi } from '../api/certificates';
import { useCourseProgressQuery, useCourseDetailQuery } from '../hooks/useCourses';
import { Enrollment } from '../types/transactions';

// Componente secundario para renderizar la tarjeta con su consulta individual de progreso y detalles
const EnrolledCourseCard: React.FC<{ enrollment: Enrollment }> = ({ enrollment }) => {
  const { t } = useTranslation();
  const { data: course, isLoading: courseLoading } = useCourseDetailQuery(enrollment.course_id);
  const { data: progress, isLoading: progressLoading } = useCourseProgressQuery(enrollment.course_id);

  if (courseLoading || progressLoading) {
    return (
      <div className="bg-background-card border border-zinc-800 rounded-2xl p-5 h-44 animate-pulse flex flex-col justify-between">
        <div className="h-4 bg-zinc-800 rounded w-2/3 mb-2"></div>
        <div className="h-2 bg-zinc-800 rounded w-full mb-4"></div>
        <div className="h-8 bg-zinc-800 rounded w-24"></div>
      </div>
    );
  }

  if (!course) return null;

  const percentage = progress?.percentage || 0;

  return (
    <div className="glass-effect border border-zinc-800/80 rounded-2xl p-5 shadow-lg flex flex-col justify-between gap-4">
      <div>
        <span className="text-[10px] font-mono font-bold text-primary-light uppercase tracking-wider">
          {course.nivel_dificultad || 'Intermedio'}
        </span>
        <h3 className="font-bold text-base text-white mt-1 truncate">{course.title}</h3>
        <p className="text-xs text-text-secondary line-clamp-2 mt-1">{course.description}</p>
      </div>

      {/* Barra de progreso */}
      <div className="space-y-1">
        <div className="flex justify-between text-xs text-text-secondary font-mono">
          <span>{t('dashboard.progress')}</span>
          <span>{percentage}%</span>
        </div>
        <div className="w-full bg-zinc-900 h-2 rounded-full overflow-hidden border border-zinc-800">
          <div
            className="bg-primary h-full transition-all duration-300"
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
      </div>

      <div className="flex justify-between items-center border-t border-zinc-850 pt-3 mt-1">
        <Link
          to={`/courses/${course.id}/learn`}
          className="px-4 py-2 bg-zinc-800 hover:bg-primary text-white text-xs font-semibold rounded-xl transition shadow-md"
        >
          {t('dashboard.go_to_class')}
        </Link>
        {percentage === 100 && (
          <span className="text-[10px] font-mono text-emerald-400 font-bold bg-emerald-950/20 px-2.5 py-1 rounded-full border border-emerald-500/20">
            {t('dashboard.completed')}
          </span>
        )}
      </div>
    </div>
  );
};

export const StudentDashboard: React.FC = () => {
  const { t } = useTranslation();
  // Consulta de inscripciones
  const { data: enrollmentsData, isLoading, error } = useQuery({
    queryKey: ['enrollments'],
    queryFn: () => transactionsApi.getEnrollments(),
  });

  const enrollments: Enrollment[] = Array.isArray(enrollmentsData?.results)
    ? enrollmentsData!.results
    : Array.isArray(enrollmentsData)
    ? (enrollmentsData as unknown as Enrollment[])
    : [];

  // Filtrar cursos completados para simulación de certificados
  // (En un caso real, cada certificado vendría del certificate-service)
  // Consulta de certificados reales
  const { data: certificates, isLoading: certsLoading, isError: certsError } = useQuery({
    queryKey: ['my-certificates'],
    queryFn: () => certificatesApi.getMyCertificates(),
  });

  // Badges de gamificación ganadas
  const badges = [
    { id: 'b1', name: 'Primer Paso', icon: '🌱', desc: 'Te inscribiste a tu primer curso' },
    { id: 'b2', name: 'Explorador', icon: '🧭', desc: 'Exploraste más de 3 categorías' },
    { id: 'b3', name: 'Pythonista', icon: '🐍', desc: 'Completaste Python Fundamentals' },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh] bg-background-deep text-text-primary">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
          <p className="text-text-secondary">Cargando tu área académica...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-12 bg-red-950/20 border border-red-900/50 rounded-2xl text-red-200 mt-8">
        <p className="font-semibold text-lg">Error al cargar el panel de estudios</p>
        <p className="text-sm text-text-secondary mt-1">Recarga la página o intenta más tarde.</p>
      </div>
    );
  }

  return (
    <div className="space-y-10 mt-4">
      {/* Saludo */}
      <div>
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">{t('dashboard.title')}</h1>
        <p className="text-text-secondary mt-2">{t('dashboard.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Lista de cursos inscritos (Columna Principal Izquierda) */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-2xl font-bold tracking-tight text-white">{t('dashboard.my_courses')}</h2>
          {enrollments.length === 0 ? (
            <div className="text-center py-16 bg-background-card border border-zinc-800 rounded-2xl space-y-4">
              <p className="text-text-secondary">{t('dashboard.no_courses')}</p>
              <Link
                to="/courses"
                className="inline-block px-5 py-2.5 bg-primary hover:bg-primary-dark text-white text-xs font-semibold rounded-xl transition"
              >
                {t('dashboard.find_courses')}
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {enrollments.map((enrollment) => (
                <EnrolledCourseCard key={enrollment.id} enrollment={enrollment} />
              ))}
            </div>
          )}
        </div>

        {/* Certificados y Logros (Columna Lateral Derecha) */}
        <div className="space-y-8">
          {/* Certificados */}
          <div className="p-6 rounded-2xl border border-zinc-800 bg-background-card space-y-4">
            <h3 className="text-lg font-bold text-white">{t('dashboard.certificates')}</h3>
            {certsLoading ? (
              <div className="flex justify-center py-4">
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-primary"></div>
              </div>
            ) : certsError ? (
              <p className="text-xs text-red-400">No pudimos cargar los certificados. Intenta de nuevo.</p>
            ) : (Array.isArray(certificates) ? certificates : []).length === 0 ? (
              <p className="text-xs text-text-muted italic">{t('dashboard.cert_notice')}</p>
            ) : (
              <div className="space-y-3">
                {(Array.isArray(certificates) ? certificates : []).map((cert) => {
                  const dateObj = new Date(cert.fecha_emision);
                  const meses = [
                    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
                  ];
                  const formattedDate = `${dateObj.getDate()} de ${meses[dateObj.getMonth()]}, ${dateObj.getFullYear()}`;

                  return (
                    <div key={cert.id} className="p-3 bg-zinc-900 border border-zinc-800 rounded-xl space-y-2">
                      <p className="text-xs font-bold text-white truncate">{cert.course_title}</p>
                      <p className="text-[10px] text-text-muted">Emitido el {formattedDate}</p>
                      <div className="flex justify-between items-center pt-2">
                        <Link
                          to={`/certificates/${cert.codigo_verificacion}/verify`}
                          className="text-[10px] text-primary-light hover:underline font-mono"
                        >
                          {t('dashboard.verify')} ({cert.codigo_verificacion})
                        </Link>
                        <a
                          href={cert.pdf_url?.startsWith('http') ? cert.pdf_url : `/api/certificates/${cert.id}/pdf`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2.5 py-1 bg-zinc-800 hover:bg-zinc-700 text-[10px] font-semibold rounded-lg text-white text-center transition"
                        >
                          {t('dashboard.download')}
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Gamificación (Badges) */}
          <div className="p-6 rounded-2xl border border-zinc-800 bg-background-card space-y-4">
            <h3 className="text-lg font-bold text-white">{t('dashboard.badges')}</h3>
            <div className="grid grid-cols-1 gap-3">
              {badges.map((badge) => (
                <div key={badge.id} className="flex items-center gap-3 p-3 bg-zinc-900/50 border border-zinc-850 rounded-xl">
                  <span className="text-2xl">{badge.icon}</span>
                  <div>
                    <h4 className="text-xs font-bold text-white">{badge.name}</h4>
                    <p className="text-[10px] text-text-muted mt-0.5">{badge.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
