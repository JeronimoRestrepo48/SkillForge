import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useCourseDetailQuery, useCourseProgressQuery } from '../hooks/useCourses';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';
import { certificatesApi } from '../api/certificates';
import { useAuth } from '../context/AuthContext';
import { Lesson } from '../types/catalog';

export const VideoPlayer: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const courseId = Number(id);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { user } = useAuth();

  // Estados locales
  const [activeLesson, setActiveLesson] = useState<Lesson | null>(null);
  const [showCelebration, setShowCelebration] = useState(false);

  // Consultas de datos
  const { data: course, isLoading: courseLoading } = useCourseDetailQuery(courseId);
  const { data: progress, isLoading: progressLoading } = useCourseProgressQuery(courseId);

  // Mutación para completar la lección
  const completeLessonMutation = useMutation({
    mutationFn: (lessonId: number) => catalogApi.completeLesson(lessonId),
    onSuccess: () => {
      // Invalidar caché del progreso para recargar los checks e IDs completados
      queryClient.invalidateQueries({ queryKey: ['courseProgress', courseId] });
      
      // Si con esta completación llegamos al total, mostrar celebración
      if (progress && progress.completed_lessons + 1 === progress.total_lessons) {
        setShowCelebration(true);
        if (user?.id) {
          certificatesApi.checkAndIssue({ user_id: user.id, course_id: courseId })
            .catch(err => console.error('Error generating certificate:', err));
        }
      }
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || 'Error al completar la lección.');
    },
  });

  // Efecto para inicializar la lección activa (primera lección del primer módulo con lecciones)
  useEffect(() => {
    if (course && (Array.isArray(course.modules) ? course.modules : []).length > 0 && !activeLesson) {
      for (const mod of (Array.isArray(course.modules) ? course.modules : [])) {
        if ((Array.isArray(mod.lessons) ? mod.lessons : []).length > 0) {
          const firstLesson = (Array.isArray(mod.lessons) ? mod.lessons : [])[0];
          if (firstLesson.content_type === 'QUIZ') {
            navigate(`/courses/${courseId}/lessons/${firstLesson.id}/quiz`);
          } else {
            setActiveLesson(firstLesson);
          }
          break;
        }
      }
    }
  }, [course, activeLesson, navigate, courseId]);

  const handleLessonSelect = (lesson: Lesson) => {
    if (lesson.content_type === 'QUIZ') {
      navigate(`/courses/${courseId}/lessons/${lesson.id}/quiz`);
    } else {
      setActiveLesson(lesson);
    }
  };

  const handleCompleteClick = () => {
    if (activeLesson) {
      completeLessonMutation.mutate(activeLesson.id);
    }
  };

  if (courseLoading || progressLoading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh] bg-background-deep text-text-primary">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
          <p className="text-text-secondary">Abriendo el aula virtual...</p>
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="text-center p-12 bg-red-950/20 border border-red-900/50 rounded-2xl text-red-200 mt-8">
        <h2 className="text-lg font-bold">Curso no disponible</h2>
        <p className="text-sm text-text-secondary mt-1">No pudimos cargar la lección activa.</p>
        <Link to="/dashboard" className="mt-4 inline-block px-6 py-2 bg-zinc-800 text-white rounded-xl text-xs">
          Volver a mis estudios
        </Link>
      </div>
    );
  }

  // URL del video de test (fallback público para reproducir)
  const videoUrl =
    activeLesson?.video_url ||
    'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4';

  const isCompleted = progress?.completed_lesson_ids?.includes(activeLesson?.id || 0) || false;

  return (
    <div className="flex flex-col lg:flex-row gap-6 mt-4 min-h-[75vh]">
      {/* Sidebar de Módulos (Izquierda) */}
      <div className="w-full lg:w-80 flex flex-col gap-4 border border-zinc-800 bg-background-card rounded-2xl p-5 shadow-lg max-h-[80vh] overflow-y-auto">
        <div>
          <h2 className="font-extrabold text-lg text-white truncate">{course.title}</h2>
          <p className="text-xs text-text-muted mt-1">Avance académico</p>
        </div>

        {/* Barra de Progreso en porcentaje */}
        {progress && (
          <div className="space-y-1.5 border-b border-zinc-850 pb-4">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-text-secondary">Progreso</span>
              <span className="text-primary-light font-mono">{progress.percentage}%</span>
            </div>
            <div className="w-full bg-zinc-900 h-2.5 rounded-full overflow-hidden border border-zinc-800">
              <div
                className="bg-primary h-full transition-all duration-300"
                style={{ width: `${progress.percentage}%` }}
              ></div>
            </div>
            <p className="text-[10px] text-text-muted">
              {progress.completed_lessons} de {progress.total_lessons} lecciones finalizadas
            </p>
          </div>
        )}

        {/* Listado de Módulos */}
        <div className="space-y-4 flex-1">
          {(Array.isArray(course.modules) ? course.modules : []).map((mod, modIdx) => (
            <div key={mod.id} className="space-y-2">
              <h3 className="text-xs font-mono font-bold text-primary-light uppercase tracking-wider">
                MÓDULO {modIdx + 1}: {mod.title}
              </h3>
              <div className="space-y-1 pl-2 border-l border-zinc-850">
                {(Array.isArray(mod.lessons) ? mod.lessons : []).length === 0 ? (
                  <p className="text-xs text-text-muted italic px-2 py-1">Sin lecciones.</p>
                ) : (
                  (Array.isArray(mod.lessons) ? mod.lessons : []).map((lesson) => {
                    const isActive = activeLesson?.id === lesson.id;
                    const isLessonDone = progress?.completed_lesson_ids?.includes(lesson.id) || false;

                    return (
                      <button
                        key={lesson.id}
                        onClick={() => handleLessonSelect(lesson)}
                        className={`w-full text-left px-3 py-2 rounded-xl text-xs transition flex items-center justify-between gap-2 ${
                          isActive
                            ? 'bg-primary/20 border border-primary/40 text-white font-semibold'
                            : 'hover:bg-zinc-850 text-text-secondary'
                        }`}
                      >
                        <span className="truncate">
                          {lesson.content_type === 'QUIZ' && '📝 '}
                          {lesson.title}
                        </span>
                        {isLessonDone && (
                          <span className="text-primary-light font-bold text-sm" title="Completada">
                            ✓
                          </span>
                        )}
                      </button>
                    );
                  })
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Reproductor y Contenido (Derecha / Centro) */}
      <div className="flex-1 flex flex-col gap-5 border border-zinc-800 bg-background-card rounded-2xl p-6 shadow-lg">
        {activeLesson ? (
          <div className="space-y-5 flex-1 flex flex-col">
            {/* Título de lección */}
            <div className="border-b border-zinc-850 pb-4">
              <span className="text-xs font-mono text-text-muted">LECCIÓN REPRODUCIÉNDOSE</span>
              <h2 className="text-xl md:text-2xl font-bold text-white mt-1">{activeLesson.title}</h2>
            </div>

            {/* Reproductor de Video */}
            <div className="relative aspect-video rounded-2xl overflow-hidden bg-black border border-zinc-850 shadow-inner">
              <video
                key={activeLesson.id} // Forza al navegador a recargar el elemento <video> al cambiar de lección
                src={videoUrl}
                controls
                className="w-full h-full object-contain"
              />
            </div>

            {/* Barra inferior de acciones */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pt-4 border-t border-zinc-850">
              <p className="text-xs text-text-secondary max-w-md">
                Completa esta lección para sumar progreso general en tu curso y habilitar la expedición del certificado.
              </p>
              
              {isCompleted ? (
                <span className="px-6 py-2.5 bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 font-semibold rounded-xl text-xs flex items-center gap-2">
                  ✓ Completada
                </span>
              ) : (
                <button
                  onClick={handleCompleteClick}
                  disabled={completeLessonMutation.isPending}
                  className="px-6 py-2.5 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl text-xs transition duration-200 disabled:opacity-50"
                >
                  {completeLessonMutation.isPending ? 'Procesando...' : 'Marcar como completada'}
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center min-h-[40vh] text-center">
            <p className="text-text-secondary">Selecciona una lección para iniciar tu aprendizaje</p>
          </div>
        )}
      </div>

      {/* Modal de Felicitaciones Animado (Glassmorphism + transform will-change) */}
      {showCelebration && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 animate-fade-in backdrop-blur-sm">
          <div className="glass-effect border border-zinc-800 p-8 rounded-3xl max-w-md w-full text-center space-y-6 shadow-2xl relative animate-scale-up">
            {/* Glow */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-48 bg-primary/10 rounded-full blur-3xl -z-10"></div>
            
            <div className="text-5xl animate-bounce">🏆</div>
            <div className="space-y-2">
              <h2 className="text-2xl font-extrabold text-white">¡Felicitaciones!</h2>
              <p className="text-text-secondary text-sm">
                Ha completado con éxito todas las lecciones del curso <strong className="text-white">{course.title}</strong>.
              </p>
            </div>
            
            <p className="text-xs text-text-muted">
              Tu rendimiento ha sido excelente. El certificado oficial ya ha sido emitido de manera digital y está disponible en tu dashboard académico.
            </p>

            <button
              onClick={() => {
                setShowCelebration(false);
                window.location.href = '/dashboard';
              }}
              className="w-full py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl transition shadow-md text-xs"
            >
              Ir a mi Dashboard para descargar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoPlayer;
