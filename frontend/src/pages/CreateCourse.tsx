import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { catalogApi } from '../api/catalog';
import { Category } from '../types/catalog';

interface CourseFormInputs {
  title: string;
  description: string;
  category_id: number;
  price: number;
  nivel_dificultad: string;
  duracion_horas: number;
}

const CreateCourse: React.FC = () => {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<CourseFormInputs>();
  const [categories, setCategories] = useState<Category[]>([]);
  const [apiError, setApiError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        // Fetch categories without pagination to get all options (or a large enough page_size)
        const res = await catalogApi.getCategories({ page_size: 100 });
        setCategories(res.results);
      } catch (err) {
        console.error('Error fetching categories:', err);
      }
    };
    fetchCategories();
  }, []);

  const onSubmit = async (data: CourseFormInputs) => {
    try {
      setApiError(null);
      // Ensure numeric values
      const payload = {
        ...data,
        category_id: Number(data.category_id),
        price: Number(data.price),
        duracion_horas: Number(data.duracion_horas)
      };
      
      const newCourse = await catalogApi.createCourse(payload);
      
      // User preferred to redirect to the edit page to add modules immediately
      navigate(`/instructor/courses/${newCourse.id}/edit`);
    } catch (err: any) {
      setApiError(err.response?.data?.detail || 'Error al crear el curso. Inténtalo de nuevo.');
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <div className="bg-background-card border border-zinc-800 rounded-2xl p-8 glass-effect shadow-2xl relative overflow-hidden">
        {/* Glow effect */}
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent-primary to-accent-secondary"></div>
        
        <h1 className="text-3xl font-extrabold mb-2 bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">Crear Nuevo Curso</h1>
        <p className="text-text-secondary mb-8">Comienza a compartir tu conocimiento creando un nuevo curso.</p>

        {apiError && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400">
            {apiError}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-zinc-300 mb-2">Título del Curso</label>
              <input
                type="text"
                {...register('title', { required: 'El título es obligatorio' })}
                className="w-full bg-background-dark border border-zinc-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50 transition-all"
                placeholder="Ej. Curso de React Moderno"
              />
              {errors.title && <p className="text-red-400 text-sm mt-1">{errors.title.message}</p>}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-zinc-300 mb-2">Descripción</label>
              <textarea
                {...register('description', { required: 'La descripción es obligatoria' })}
                className="w-full bg-background-dark border border-zinc-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50 transition-all h-32 resize-none"
                placeholder="Explica qué aprenderán los estudiantes..."
              />
              {errors.description && <p className="text-red-400 text-sm mt-1">{errors.description.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">Categoría</label>
              <select
                {...register('category_id', { required: 'Selecciona una categoría' })}
                className="w-full bg-background-dark border border-zinc-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50 transition-all appearance-none"
              >
                <option value="">-- Seleccionar --</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
              {errors.category_id && <p className="text-red-400 text-sm mt-1">{errors.category_id.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">Nivel de Dificultad</label>
              <select
                {...register('nivel_dificultad', { required: 'Selecciona un nivel' })}
                className="w-full bg-background-dark border border-zinc-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50 transition-all appearance-none"
              >
                <option value="PRINCIPIANTE">Principiante</option>
                <option value="INTERMEDIO">Intermedio</option>
                <option value="AVANZADO">Avanzado</option>
              </select>
              {errors.nivel_dificultad && <p className="text-red-400 text-sm mt-1">{errors.nivel_dificultad.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">Precio (USD)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                {...register('price', { required: 'El precio es obligatorio', min: 0 })}
                className="w-full bg-background-dark border border-zinc-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50 transition-all"
                placeholder="0.00"
              />
              {errors.price && <p className="text-red-400 text-sm mt-1">{errors.price.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">Duración Estimada (Horas)</label>
              <input
                type="number"
                min="0"
                {...register('duracion_horas', { required: 'La duración es obligatoria', min: 0 })}
                className="w-full bg-background-dark border border-zinc-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50 transition-all"
                placeholder="10"
              />
              {errors.duracion_horas && <p className="text-red-400 text-sm mt-1">{errors.duracion_horas.message}</p>}
            </div>
          </div>

          <div className="pt-6 border-t border-zinc-800 flex justify-end gap-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="px-6 py-3 rounded-xl font-semibold text-zinc-300 hover:text-white hover:bg-white/5 transition-all"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-3 rounded-xl font-semibold text-white bg-accent-primary hover:bg-accent-primary/90 transition-all shadow-[0_0_15px_rgba(235,93,61,0.3)] disabled:opacity-50"
            >
              {isSubmitting ? 'Creando...' : 'Crear Curso'}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};

export default CreateCourse;
