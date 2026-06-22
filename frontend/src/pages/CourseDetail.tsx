import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { useCourseDetailQuery, useCourseProgressQuery } from '../hooks/useCourses';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionsApi } from '../api/transactions';
import { catalogApi } from '../api/catalog';
import { getCategoryImage } from './Home';
import { FadeInSection } from '../components/FadeInSection';
import { SkeletonDetailHeader } from '../components/SkeletonCard';

export const CourseDetail: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const courseId = Number(id);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Acordeón: id del módulo abierto (por defecto el primero o ninguno)
  const [openModuleId, setOpenModuleId] = useState<number | null>(null);

  // Consulta de los detalles del curso
  const { data: course, isLoading, error } = useCourseDetailQuery(courseId);

  // Consulta de inscripciones si el usuario está logueado
  const { data: enrollmentsData } = useQuery({
    queryKey: ['enrollments'],
    queryFn: () => transactionsApi.getEnrollments(),
    enabled: isAuthenticated,
  });

  const { data: certProgress } = useQuery({
    queryKey: ['certProgress', courseId],
    queryFn: () => catalogApi.getCertificationProgress(courseId),
    enabled: isAuthenticated && course?.es_certificacion === true,
  });

  const { data: progress } = useCourseProgressQuery(courseId);

  // Mutación para agregar al carrito
  const addToCartMutation = useMutation({
    mutationFn: () => transactionsApi.addToCart({ course_id: courseId, quantity: 1 }),
    onSuccess: () => {
      // Invalidar query del carrito para que se recargue
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      navigate('/cart');
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || 'Error al agregar al carrito.');
    },
  });

  // Fetch de reseñas
  const { data: reviews, refetch: refetchReviews } = useQuery({
    queryKey: ['reviews', courseId],
    queryFn: () => catalogApi.getReviews(courseId),
  });

  // Estado local para el formulario de reseña
  const [reviewScore, setReviewScore] = useState<number>(5);
  const [reviewComment, setReviewComment] = useState('');
  const [reviewSubmitted, setReviewSubmitted] = useState(false);

  // Mutación para enviar reseña
  const submitReviewMutation = useMutation({
    mutationFn: () => catalogApi.submitReview(courseId, { score: reviewScore, comment: reviewComment }),
    onSuccess: () => {
      setReviewComment('');
      setReviewScore(5);
      setReviewSubmitted(true);
      refetchReviews();
      queryClient.invalidateQueries({ queryKey: ['courseDetail', courseId] });
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || 'Error al enviar la reseña.');
    },
  });

  const isEnrolled = enrollmentsData?.results.some(
    (enrollment) => enrollment.course_id === courseId && enrollment.status === 'ACTIVA'
  );

  const handleBuyClick = () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: { pathname: `/courses/${courseId}` } } });
      return;
    }
    addToCartMutation.mutate();
  };

  const toggleModule = (moduleId: number) => {
    setOpenModuleId(openModuleId === moduleId ? null : moduleId);
  };

  if (isLoading) {
    return (
      <div className="space-y-8 mt-4">
        <SkeletonDetailHeader />
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="text-center p-12 bg-red-950/20 border border-red-900/50 rounded-2xl text-red-200 mt-8">
        <p className="font-semibold text-lg">Curso no encontrado</p>
        <p className="text-sm text-text-secondary mt-1">El curso solicitado no existe o no se encuentra disponible.</p>
        <Link to="/courses" className="mt-4 inline-block px-6 py-2 bg-zinc-800 text-white rounded-xl text-xs hover:bg-zinc-700">
          Volver al catálogo
        </Link>
      </div>
    );
  }

  // Imagen de fondo segun la categoria del curso
  const categoryName = typeof (course as any).categoria === 'object'
    ? ((course as any).categoria?.name || '')
    : '';
  const headerImg = getCategoryImage(categoryName || course.title);

  return (
    <div className="space-y-8 mt-4">
      {/* Header con imagen Unsplash de fondo */}
      <div
        className="relative rounded-3xl overflow-hidden border border-zinc-800 shadow-2xl"
        style={{ minHeight: '320px' }}
      >
        {/* Imagen de fondo */}
        <div
          style={{
            position: 'absolute', inset: 0,
            backgroundImage: `url('${headerImg}')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />
        {/* Overlay oscuro */}
        <div
          style={{
            position: 'absolute', inset: 0,
            background: 'linear-gradient(135deg, rgba(10,10,10,0.88) 0%, rgba(10,10,10,0.72) 60%, rgba(10,10,10,0.92) 100%)',
          }}
        />
        {/* Borde izquierdo verde */}
        <div
          style={{
            position: 'absolute', left: 0, top: 0, bottom: 0, width: '3px',
            background: '#39FF14',
          }}
        />
        {/* Contenido del header */}
        <div style={{ position: 'relative', zIndex: 1 }} className="p-8 md:p-12">
          <div className="max-w-3xl space-y-6">
          <span className="text-primary-light font-mono text-xs uppercase tracking-wider bg-primary/20 px-3 py-1 rounded-full border border-primary/30">
            {course.nivel_dificultad || 'Intermedio'}
          </span>
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white">{course.title}</h1>
          {i18n.language !== 'es' && t('catalog.content_language_notice') && (
            <p className="text-xs text-zinc-500 italic mt-1">
              {t('catalog.content_language_notice')}
            </p>
          )}
          <p className="text-text-secondary text-base md:text-lg leading-relaxed">
            {course.description || 'Domina los conceptos fundamentales y adquiere experiencia práctica con este curso guiado.'}
          </p>
          
          {/* Metadatos */}
          <div className="flex flex-wrap gap-6 text-sm text-text-secondary pt-2">
            <span>🕒 {t('catalog.duration')}: <strong>{course.duracion_horas || 12} {t('catalog.hours')}</strong></span>
            <span>⭐ {t('course.score')}: <strong>{course.average_rating ? `${course.average_rating.toFixed(1)}/5` : 'Sin calificación'}</strong></span>
            <span>👥 {t('course.students')}: <strong>{course.rating_count || 0} {t('catalog.ratings')}</strong></span>
            {course.instructor_id && (
              <span>👤 {t('course.instructor')}: <strong><Link to={`/instructors/${course.instructor_id}`} className="hover:text-primary transition underline decoration-zinc-700 underline-offset-4">Ver Perfil</Link></strong></span>
            )}
          </div>

          {/* Botones de acción */}
          <div className="flex flex-wrap gap-4 items-center pt-4 border-t border-zinc-800/80">
            <span className="text-2xl font-mono font-extrabold text-white">
              {course.price === 0 ? t('catalog.free') : `$${Number(course.price).toLocaleString('es-CO')} COP`}
            </span>
            
            {isEnrolled ? (
              <motion.div whileTap={{ scale: 0.96 }} transition={{ type: 'spring', stiffness: 400, damping: 25 }} style={{ display: 'inline-block' }}>
                <Link
                  to={`/courses/${course.id}/learn`}
                  className="px-8 py-3.5 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl shadow-lg transition duration-200 inline-block"
                >
                  {t('catalog.continue')}
                </Link>
              </motion.div>
            ) : (
              <motion.button
                whileTap={{ scale: 0.96 }}
                transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                onClick={handleBuyClick}
                disabled={addToCartMutation.isPending}
                className="px-8 py-3.5 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl shadow-lg transition duration-200 disabled:opacity-50"
              >
                {addToCartMutation.isPending ? 'Procesando...' : t('catalog.buy')}
              </motion.button>
            )}
          </div>
          </div>
        </div>
      </div>

      {/* Grid de contenido */}
      <FadeInSection delay={0}>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Temario (Módulos y Lecciones) */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-2xl font-bold tracking-tight">{t('course.content')}</h2>
          
          {(Array.isArray(course.modules) ? course.modules : []).length === 0 ? (
            <p className="text-text-muted text-sm italic">{t('course.no_modules')}</p>
          ) : (
            <div className="space-y-3">
              {(Array.isArray(course.modules) ? course.modules : []).map((mod, index) => {
                const isOpen = openModuleId === mod.id;
                const modStatus = certProgress?.modules?.find(m => m.module_id === mod.id);
                const isLocked = course.es_certificacion && modStatus?.bloqueado;

                return (
                  <div key={mod.id} className={`border border-zinc-800/80 rounded-xl overflow-hidden transition ${isLocked ? 'bg-zinc-900/40 opacity-75' : 'bg-background-card'}`}>
                    <button
                      onClick={() => !isLocked && toggleModule(mod.id)}
                      className={`w-full px-5 py-4 flex justify-between items-center text-left transition ${isLocked ? 'cursor-not-allowed' : 'hover:bg-zinc-850/50'}`}
                    >
                      <div className="flex items-center gap-3">
                        {isLocked && <span className="text-zinc-500 text-xl">🔒</span>}
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs text-primary-light font-mono font-semibold">
                              {t('course.module')} {index + 1}
                            </span>
                            {course.es_certificacion && (mod.es_examen_modulo || modStatus?.es_examen_modulo) && (
                              <span className="px-2 py-0.5 text-[10px] uppercase font-bold bg-primary/20 text-primary border border-primary/30 rounded-full">
                                {t('course.exam_module')}
                              </span>
                            )}
                            {course.es_certificacion && (mod.es_examen_final || modStatus?.es_examen_final) && (
                              <span className="px-2 py-0.5 text-[10px] uppercase font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30 rounded-full">
                                {t('course.final_exam')}
                              </span>
                            )}
                            {modStatus?.aprobado && (
                              <span className="text-primary text-sm" title="Aprobado">✅</span>
                            )}
                          </div>
                          <span className={`font-bold text-sm sm:text-base ${isLocked ? 'text-zinc-400' : 'text-white'}`}>{mod.title}</span>
                        </div>
                      </div>
                      <span className={`text-xl transition duration-200 ${isOpen ? 'rotate-180' : ''} ${isLocked ? 'text-zinc-600' : 'text-text-muted'}`}>
                        ▼
                      </span>
                    </button>

                    {isOpen && (
                      <div className="border-t border-zinc-850/50 bg-background-dark/30 divide-y divide-zinc-850/30">
                        {(Array.isArray(mod.lessons) ? mod.lessons : []).length === 0 ? (
                          <div className="px-5 py-3 text-xs text-text-muted italic">No hay lecciones en este módulo.</div>
                        ) : (
                          (Array.isArray(mod.lessons) ? mod.lessons : []).map((lesson) => {
                            const isQuiz = lesson.content_type === 'QUIZ';
                            return (
                              <div key={lesson.id} className="px-5 py-3 flex justify-between items-center hover:bg-zinc-850/20 transition">
                                <div className="flex items-center gap-3">
                                  {progress?.completed_lesson_ids?.includes(lesson.id) ? (
                                    <span className="text-emerald-400 text-sm font-bold" title="Completada">✓</span>
                                  ) : (
                                    <span className="text-text-muted text-sm font-mono">
                                      {lesson.sort_order}.
                                    </span>
                                  )}
                                  {isQuiz ? (
                                    <Link 
                                      to={isLocked ? '#' : `/courses/${courseId}/lessons/${lesson.id}/quiz`}
                                      className={`text-sm font-semibold flex items-center gap-2 ${isLocked ? 'text-zinc-500 cursor-not-allowed pointer-events-none' : 'text-primary hover:text-primary-light underline underline-offset-2 decoration-primary/50'}`}
                                    >
                                      📝 {lesson.title}
                                    </Link>
                                  ) : (
                                    <span className={`text-sm ${isLocked ? 'text-zinc-500' : progress?.completed_lesson_ids?.includes(lesson.id) ? 'text-text-secondary line-through' : 'text-text-secondary'}`}>{lesson.title}</span>
                                  )}
                                </div>
                                {lesson.duration && (
                                  <span className="text-xs text-text-muted font-mono">
                                    ⏱️ {lesson.duration} min
                                  </span>
                                )}
                              </div>
                            );
                          })
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Panel lateral de información adicional */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl border border-zinc-800 bg-background-card space-y-4">
            <h3 className="text-lg font-bold text-white">{t('course.includes')}:</h3>
            <ul className="space-y-3 text-sm text-text-secondary">
              <li className="flex items-center gap-2">🟢 {t('course.unlimited_access')}</li>
              <li className="flex items-center gap-2">🟢 {t('course.support')}</li>
              <li className="flex items-center gap-2">🟢 {t('course.evaluations')}</li>
              <li className="flex items-center gap-2">🟢 {t('course.certificate')}</li>
            </ul>
          </div>
        </div>
      </div>
      </FadeInSection>

      <FadeInSection delay={0.1}>
      <div className="space-y-6 mt-8">
        <h2 className="text-2xl font-bold tracking-tight">{t('course.reviews')}</h2>

        {/* Resumen de calificación */}
        <div className="flex items-center gap-6 p-6 rounded-2xl border border-zinc-800 bg-background-card">
          <div className="text-center">
            <div className="text-5xl font-extrabold text-white">
              {course.average_rating ? course.average_rating.toFixed(1) : '—'}
            </div>
            <div className="text-primary text-xl mt-1">
              {'★'.repeat(Math.round(course.average_rating || 0))}{'☆'.repeat(5 - Math.round(course.average_rating || 0))}
            </div>
            <div className="text-xs text-text-muted mt-1">{course.rating_count || 0} {t('catalog.ratings')}</div>
          </div>
        </div>

        {/* Formulario para dejar reseña — solo si está inscrito y autenticado */}
        {isAuthenticated && isEnrolled && !reviewSubmitted && (
          <div className="p-6 rounded-2xl border border-zinc-800 bg-background-card space-y-4">
            <h3 className="text-lg font-bold text-white">{t('course.leave_review')}</h3>
            {/* Selector de estrellas */}
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setReviewScore(star)}
                  className={`text-3xl transition ${star <= reviewScore ? 'text-primary' : 'text-zinc-600 hover:text-zinc-400'}`}
                >
                  ★
                </button>
              ))}
            </div>
            <textarea
              value={reviewComment}
              onChange={(e) => setReviewComment(e.target.value)}
              placeholder={t('course.review_placeholder')}
              rows={3}
              className="w-full bg-zinc-900 border border-zinc-700 rounded-xl p-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-primary resize-none"
            />
            <motion.button
              whileTap={{ scale: 0.96 }}
              transition={{ type: 'spring', stiffness: 400, damping: 25 }}
              onClick={() => submitReviewMutation.mutate()}
              disabled={!reviewComment.trim() || submitReviewMutation.isPending}
              className="px-6 py-2.5 bg-primary hover:bg-primary-dark text-black font-semibold rounded-xl text-sm disabled:opacity-50 transition"
            >
              {submitReviewMutation.isPending ? 'Enviando...' : t('course.publish_review')}
            </motion.button>
          </div>
        )}
        {reviewSubmitted && (
          <div className="p-4 rounded-xl border border-primary/30 bg-primary/10 text-primary text-sm font-semibold">
            {t('course.review_success')}
          </div>
        )}

        {/* Lista de reseñas */}
        <div className="space-y-4">
          {(!reviews || reviews.length === 0) ? (
            <p className="text-text-muted text-sm italic">{t('course.no_reviews')}</p>
          ) : (
            reviews.map((review: any) => (
              <div key={review.id} className="p-5 rounded-xl border border-zinc-800 bg-background-card space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-primary font-mono font-bold text-sm">
                      {'★'.repeat(review.score)}{'☆'.repeat(5 - review.score)}
                    </span>
                    <span className="text-xs text-text-muted">
                      {new Date(review.created_at).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' })}
                    </span>
                  </div>
                  <span className="text-xs text-zinc-600 font-mono">Usuario #{review.user_id}</span>
                </div>
                {review.comment && (
                  <p className="text-sm text-text-secondary leading-relaxed">{review.comment}</p>
                )}
              </div>
            ))
          )}
        </div>
      </div>
      </FadeInSection>
    </div>
  );
};

export default CourseDetail;
