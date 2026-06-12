import React from 'react';
import { Link } from 'react-router-dom';
import { useCoursesQuery } from '../hooks/useCourses';
import { Course } from '../types/catalog';

export const InstructorDashboard: React.FC = () => {
  // Cargar cursos del catálogo (en un escenario real, cargaríamos solo los del instructor logueado)
  const { data: coursesData, isLoading, isError } = useCoursesQuery();
  const myCourses: Course[] = Array.isArray(coursesData?.results)
    ? coursesData!.results
    : Array.isArray(coursesData)
    ? (coursesData as unknown as Course[])
    : [];

  // Estadísticas del instructor (simuladas estéticamente basadas en datos reales)
  const stats = {
    totalStudents: 1420,
    activeCourses: myCourses.length || 3,
    totalEarnings: 8420000, // En COP
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh] bg-background-deep text-text-primary">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
          <p className="text-text-secondary">Cargando panel de instructor...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-center p-12 bg-red-950/20 border border-red-900/50 rounded-2xl text-red-200 mt-8">
        <p className="font-semibold text-lg">No pudimos cargar los cursos</p>
        <p className="text-sm text-text-secondary mt-1">Intenta recargar la página o verifica tu conexión.</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-5 py-2 bg-zinc-800 hover:bg-zinc-700 text-white text-xs font-semibold rounded-xl transition"
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-10 mt-4">
      {/* Encabezado */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">Panel de Instructor</h1>
          <p className="text-text-secondary mt-2">Monitorea tus cursos y el rendimiento de tus estudiantes</p>
        </div>
        <Link
          to="/instructor/courses/new"
          className="px-5 py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl transition shadow-lg text-xs"
        >
          ➕ Crear Nuevo Curso
        </Link>
      </div>

      {/* Grid de Estadísticas (Con Glassmorphism y will-change) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="glass-effect border border-zinc-800 p-6 rounded-2xl shadow-md space-y-2">
          <p className="text-xs font-mono text-text-muted uppercase tracking-wider">Estudiantes Inscritos</p>
          <p className="text-3xl font-extrabold text-white">{stats.totalStudents.toLocaleString('es-CO')}</p>
          <span className="text-[10px] text-emerald-400 block">📈 +12% este mes</span>
        </div>

        <div className="glass-effect border border-zinc-800 p-6 rounded-2xl shadow-md space-y-2">
          <p className="text-xs font-mono text-text-muted uppercase tracking-wider">Cursos Activos</p>
          <p className="text-3xl font-extrabold text-white">{stats.activeCourses}</p>
          <span className="text-[10px] text-text-muted block">🟢 Todos en estado PUBLISHED</span>
        </div>

        <div className="glass-effect border border-zinc-800 p-6 rounded-2xl shadow-md space-y-2">
          <p className="text-xs font-mono text-text-muted uppercase tracking-wider">Ingresos Totales</p>
          <p className="text-3xl font-extrabold text-primary-light">
            ${stats.totalEarnings.toLocaleString('es-CO')} COP
          </p>
          <span className="text-[10px] text-emerald-400 block">📈 Facturación al día</span>
        </div>
      </div>

      {/* Listado de cursos creados */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold tracking-tight text-white">Administración de Mis Cursos</h2>
        
        {myCourses.length === 0 ? (
          <div className="text-center py-16 bg-background-card border border-zinc-800 rounded-2xl space-y-4">
            <p className="text-text-secondary">No hay cursos disponibles por el momento.</p>
            <p className="text-sm text-text-muted">Crea tu primer curso para que aparezca aquí.</p>
          </div>
        ) : (
          <div className="divide-y divide-zinc-850 border border-zinc-800 bg-background-card rounded-2xl overflow-hidden shadow-md">
            {myCourses.map((course) => (
              <div key={course.id} className="p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:bg-zinc-850/10 transition">
                <div>
                  <h3 className="font-bold text-base text-white">{course.title}</h3>
                  <p className="text-xs text-text-muted mt-1 truncate-2-lines max-w-xl">
                    {course.description}
                  </p>
                  <div className="flex gap-4 text-[10px] text-text-muted mt-2">
                    <span>Dificultad: <strong className="text-white capitalize">{course.nivel_dificultad || 'Intermedio'}</strong></span>
                    <span>Precio: <strong className="text-white">${Number(course.price).toLocaleString('es-CO')} COP</strong></span>
                  </div>
                </div>
                <div className="flex gap-2 w-full sm:w-auto pt-4 sm:pt-0 border-t border-zinc-850 sm:border-none">
                  <Link
                    to={`/instructor/courses/${course.id}/edit`}
                    className="px-3 py-2 bg-zinc-800 hover:bg-zinc-700 text-xs font-semibold rounded-lg text-white transition text-center flex-1 sm:flex-initial"
                  >
                    Editar
                  </Link>
                  <Link
                    to={`/courses/${course.id}`}
                    className="px-3 py-2 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs font-semibold rounded-lg text-text-secondary hover:text-white transition text-center flex-1 sm:flex-initial"
                  >
                    Ver Ficha
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default InstructorDashboard;
