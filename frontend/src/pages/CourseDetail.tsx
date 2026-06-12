import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCourseDetailQuery } from '../hooks/useCourses';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionsApi } from '../api/transactions';
import { getCategoryImage } from './Home';

export const CourseDetail: React.FC = () => {
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
      <div className="flex items-center justify-center min-h-[70vh] bg-background-deep text-text-primary">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
          <p className="text-text-secondary">Cargando detalles del curso...</p>
        </div>
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
          <p className="text-text-secondary text-base md:text-lg leading-relaxed">
            {course.description || 'Domina los conceptos fundamentales y adquiere experiencia práctica con este curso guiado.'}
          </p>
          
          {/* Metadatos */}
          <div className="flex flex-wrap gap-6 text-sm text-text-secondary pt-2">
            <span>🕒 Duración: <strong>{course.duracion_horas || 12} horas</strong></span>
            <span>⭐ Puntuación: <strong>{course.average_rating ? `${course.average_rating.toFixed(1)}/5` : 'Sin calificación'}</strong></span>
            <span>👥 Estudiantes: <strong>{course.rating_count || 0} valoraciones</strong></span>
          </div>

          {/* Botones de acción */}
          <div className="flex flex-wrap gap-4 items-center pt-4 border-t border-zinc-800/80">
            <span className="text-2xl font-mono font-extrabold text-white">
              {course.price === 0 ? 'Gratis' : `$${Number(course.price).toLocaleString('es-CO')} COP`}
            </span>
            
            {isEnrolled ? (
              <Link
                to={`/courses/${course.id}/learn`}
                className="px-8 py-3.5 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl shadow-lg transition duration-200"
              >
                Continuar aprendiendo
              </Link>
            ) : (
              <button
                onClick={handleBuyClick}
                disabled={addToCartMutation.isPending}
                className="px-8 py-3.5 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl shadow-lg transition duration-200 disabled:opacity-50"
              >
                {addToCartMutation.isPending ? 'Procesando...' : 'Comprar Curso'}
              </button>
            )}
          </div>
          </div>
        </div>
      </div>

      {/* Grid de contenido */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Temario (Módulos y Lecciones) */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-2xl font-bold tracking-tight">Contenido del Curso</h2>
          
          {(Array.isArray(course.modules) ? course.modules : []).length === 0 ? (
            <p className="text-text-muted text-sm italic">Este curso aún no tiene módulos ni lecciones publicadas.</p>
          ) : (
            <div className="space-y-3">
              {(Array.isArray(course.modules) ? course.modules : []).map((mod, index) => {
                const isOpen = openModuleId === mod.id;
                return (
                  <div key={mod.id} className="border border-zinc-800/80 rounded-xl overflow-hidden bg-background-card transition">
                    <button
                      onClick={() => toggleModule(mod.id)}
                      className="w-full px-5 py-4 flex justify-between items-center text-left hover:bg-zinc-850/50 transition"
                    >
                      <div>
                        <span className="text-xs text-primary-light font-mono font-semibold block mb-1">
                          MÓDULO {index + 1}
                        </span>
                        <span className="font-bold text-sm sm:text-base text-white">{mod.title}</span>
                      </div>
                      <span className={`text-xl text-text-muted transition duration-200 ${isOpen ? 'rotate-180' : ''}`}>
                        ▼
                      </span>
                    </button>

                    {isOpen && (
                      <div className="border-t border-zinc-850/50 bg-background-dark/30 divide-y divide-zinc-850/30">
                        {(Array.isArray(mod.lessons) ? mod.lessons : []).length === 0 ? (
                          <div className="px-5 py-3 text-xs text-text-muted italic">No hay lecciones en este módulo.</div>
                        ) : (
                          (Array.isArray(mod.lessons) ? mod.lessons : []).map((lesson) => (
                            <div key={lesson.id} className="px-5 py-3 flex justify-between items-center hover:bg-zinc-850/20 transition">
                              <div className="flex items-center gap-3">
                                <span className="text-text-muted text-sm font-mono">
                                  {lesson.sort_order}.
                                </span>
                                <span className="text-text-secondary text-sm">{lesson.title}</span>
                              </div>
                              {lesson.duration && (
                                <span className="text-xs text-text-muted font-mono">
                                  ⏱️ {lesson.duration} min
                                </span>
                              )}
                            </div>
                          ))
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
            <h3 className="text-lg font-bold text-white">Este curso incluye:</h3>
            <ul className="space-y-3 text-sm text-text-secondary">
              <li className="flex items-center gap-2">🟢 Acceso ilimitado de por vida</li>
              <li className="flex items-center gap-2">🟢 Soporte y foro de consultas</li>
              <li className="flex items-center gap-2">🟢 Evaluaciones prácticas</li>
              <li className="flex items-center gap-2">🟢 Certificación de finalización</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;
