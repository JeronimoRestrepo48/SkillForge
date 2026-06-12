import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useCoursesQuery, useCategoriesQuery } from '../hooks/useCourses';
import CourseCard from '../components/CourseCard';

export const CourseCatalog: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Estados de los filtros desde la URL
  const queryParam = searchParams.get('q') || '';
  const categoryParam = searchParams.get('categoria') ? Number(searchParams.get('categoria')) : undefined;
  const pageParam = searchParams.get('page') ? Number(searchParams.get('page')) : 1;

  const [searchTerm, setSearchTerm] = useState(queryParam);
  const [debouncedSearch, setDebouncedSearch] = useState(queryParam);

  // Implementación del Debounce de 300ms para la búsqueda en tiempo real
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 300);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm]);

  // Sincronizar URL cuando cambian el debounce de búsqueda o la categoría
  useEffect(() => {
    const params: Record<string, string> = {};
    if (debouncedSearch) params.q = debouncedSearch;
    if (categoryParam) params.categoria = String(categoryParam);
    if (pageParam > 1) params.page = String(pageParam);
    setSearchParams(params);
  }, [debouncedSearch, categoryParam, pageParam]);

  // Consultas de React Query
  const { data: coursesData, isLoading: coursesLoading, error: coursesError } = useCoursesQuery({
    q: debouncedSearch,
    categoria: categoryParam,
    page: pageParam,
    page_size: 6,
  });

  const { data: categoriesData, isLoading: categoriesLoading } = useCategoriesQuery();

  const handleCategoryClick = (id: number | undefined) => {
    const params: Record<string, string> = {};
    if (debouncedSearch) params.q = debouncedSearch;
    if (id) params.categoria = String(id);
    setSearchParams(params); // Resetea a página 1 automáticamente
  };

  const handlePageChange = (newPage: number) => {
    const params: Record<string, string> = {};
    if (debouncedSearch) params.q = debouncedSearch;
    if (categoryParam) params.categoria = String(categoryParam);
    params.page = String(newPage);
    setSearchParams(params);
  };

  return (
    <div className="space-y-8 mt-4">
      {/* Encabezado */}
      <div>
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">Catálogo de Cursos</h1>
        <p className="text-text-secondary mt-2">Explora y perfecciona tus habilidades con nuestros cursos premium</p>
      </div>

      {/* Buscador y Filtro de Categoría */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
        {/* Input Buscador */}
        <div className="relative w-full md:max-w-md">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="🔍 Buscar curso por título..."
            className="w-full px-4 py-3 bg-background-card border border-zinc-800 rounded-xl focus:outline-none focus:border-primary text-text-primary placeholder-text-muted transition shadow-inner text-sm"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-text-muted hover:text-white"
            >
              ✕
            </button>
          )}
        </div>

        {/* Chips de Categorías */}
        <div className="flex flex-wrap gap-2 w-full md:w-auto overflow-x-auto pb-2">
          <button
            onClick={() => handleCategoryClick(undefined)}
            className={`px-4 py-2 text-xs font-semibold rounded-xl border transition ${
              categoryParam === undefined
                ? 'bg-primary border-primary text-white shadow-md'
                : 'bg-zinc-900 border-zinc-800 text-text-secondary hover:text-white hover:border-zinc-700'
            }`}
          >
            Todos
          </button>
          {categoriesLoading ? (
            <div className="h-8 w-24 bg-zinc-900 animate-pulse rounded-xl"></div>
          ) : (
          (Array.isArray(categoriesData?.results) ? categoriesData!.results : []).map((category) => (
              <button
                key={category.id}
                onClick={() => handleCategoryClick(category.id)}
                className={`px-4 py-2 text-xs font-semibold rounded-xl border transition ${
                  categoryParam === category.id
                    ? 'bg-primary border-primary text-white shadow-md'
                    : 'bg-zinc-900 border-zinc-800 text-text-secondary hover:text-white hover:border-zinc-700'
                }`}
              >
                {category.name}
              </button>
            ))
          )}
        </div>
      </div>

      {/* Grid de Cursos */}
      {coursesLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="bg-background-card border border-zinc-800/80 rounded-2xl h-80 animate-pulse p-5 flex flex-col justify-between">
              <div className="h-32 bg-zinc-800/50 rounded-xl mb-4"></div>
              <div className="h-6 bg-zinc-800/50 rounded-md mb-2"></div>
              <div className="h-4 bg-zinc-800/30 rounded-md mb-4 w-3/4"></div>
              <div className="h-8 bg-zinc-800/80 rounded-xl w-full"></div>
            </div>
          ))}
        </div>
      ) : coursesError ? (
        <div className="text-center p-12 bg-red-950/20 border border-red-900/50 rounded-2xl text-red-200">
          <p className="font-semibold text-lg">No pudimos cargar los cursos. Intenta de nuevo.</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-5 py-2 bg-zinc-800 hover:bg-zinc-700 text-white text-xs font-semibold rounded-xl transition"
          >
            Reintentar
          </button>
        </div>
      ) : (Array.isArray(coursesData?.results) ? coursesData!.results : []).length === 0 ? (
        <div className="text-center py-20 bg-background-card border border-zinc-800 rounded-2xl">
          <p className="text-lg font-semibold text-text-secondary">No hay cursos disponibles por el momento.</p>
          <p className="text-sm text-text-muted mt-1">Prueba cambiando tu búsqueda o seleccionando otra categoría.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {(Array.isArray(coursesData?.results) ? coursesData!.results : []).map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}

      {/* Paginación */}
      {coursesData && coursesData.count > 0 && (
        <div className="flex justify-between items-center border-t border-zinc-900 pt-6 mt-8">
          <p className="text-xs text-text-muted">
            Mostrando {coursesData.results.length} de {coursesData.count} cursos
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => handlePageChange(pageParam - 1)}
              disabled={pageParam <= 1 || coursesLoading}
              className="px-4 py-2 bg-zinc-900 border border-zinc-800 text-xs font-semibold rounded-xl text-text-secondary hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Anterior
            </button>
            <button
              onClick={() => handlePageChange(pageParam + 1)}
              disabled={!coursesData.next || coursesLoading}
              className="px-4 py-2 bg-zinc-900 border border-zinc-800 text-xs font-semibold rounded-xl text-text-secondary hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourseCatalog;
