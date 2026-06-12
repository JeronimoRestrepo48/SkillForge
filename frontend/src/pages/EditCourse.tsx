import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { catalogApi } from '../api/catalog';
import { CourseDetail, Category } from '../types/catalog';
import { useForm } from 'react-hook-form';

const EditCourse: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  
  // States for new module/lesson forms
  const [showModuleForm, setShowModuleForm] = useState(false);
  const [newModuleTitle, setNewModuleTitle] = useState('');
  
  const [activeModuleForLesson, setActiveModuleForLesson] = useState<number | null>(null);
  const [newLessonTitle, setNewLessonTitle] = useState('');
  const [newLessonUrl, setNewLessonUrl] = useState('');

  const { register, handleSubmit, reset } = useForm();

  const fetchCourseData = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await catalogApi.getCourseDetail(Number(id));
      setCourse(data);
      reset({
        title: data.title,
        description: data.description,
        category_id: data.category_id,
        price: data.price,
        nivel_dificultad: data.nivel_dificultad,
        duracion_horas: data.duracion_horas
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar el curso.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    catalogApi.getCategories({ page_size: 100 }).then(res => setCategories(res.results)).catch(console.error);
    fetchCourseData();
  }, [id]);

  const handleUpdateCourse = async (data: any) => {
    if (!course) return;
    try {
      const payload = {
        ...data,
        category_id: Number(data.category_id),
        price: Number(data.price),
        duracion_horas: Number(data.duracion_horas),
        status: course.status
      };
      await catalogApi.updateCourse(course.id, payload);
      alert('Curso actualizado correctamente');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al actualizar el curso.');
    }
  };

  const handleCreateModule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!course || !newModuleTitle) return;
    try {
      const sortOrder = course.modules.length + 1;
      await catalogApi.createModule(course.id, { title: newModuleTitle, sort_order: sortOrder });
      setNewModuleTitle('');
      setShowModuleForm(false);
      fetchCourseData();
    } catch (err: any) {
      alert('Error al crear módulo');
    }
  };

  const handleCreateLesson = async (e: React.FormEvent, moduleId: number) => {
    e.preventDefault();
    if (!newLessonTitle || !newLessonUrl) return;
    try {
      const module = course?.modules.find(m => m.id === moduleId);
      const sortOrder = module ? module.lessons.length + 1 : 1;
      await catalogApi.createLesson(moduleId, {
        title: newLessonTitle,
        content_type: 'VIDEO',
        content: newLessonUrl,
        sort_order: sortOrder,
        duration_minutes: 5 // Default for now
      });
      setNewLessonTitle('');
      setNewLessonUrl('');
      setActiveModuleForLesson(null);
      fetchCourseData();
    } catch (err: any) {
      alert('Error al crear lección');
    }
  };

  const handleDeleteModule = async (moduleId: number) => {
    if (!course || !window.confirm('¿Seguro que deseas eliminar este módulo y todas sus lecciones?')) return;
    try {
      await catalogApi.deleteModule(course.id, moduleId);
      fetchCourseData();
    } catch (err) {
      alert('Error al eliminar módulo');
    }
  };

  const handleDeleteLesson = async (moduleId: number, lessonId: number) => {
    if (!window.confirm('¿Seguro que deseas eliminar esta lección?')) return;
    try {
      await catalogApi.deleteLesson(moduleId, lessonId);
      fetchCourseData();
    } catch (err) {
      alert('Error al eliminar lección');
    }
  };

  if (loading) return <div className="p-8 text-center text-zinc-400">Cargando...</div>;
  if (error || !course) return <div className="p-8 text-center text-red-500">{error}</div>;

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 space-y-8">
      {/* Basic Info Section */}
      <div className="bg-background-card border border-zinc-800 rounded-2xl p-8 glass-effect shadow-xl relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent-primary to-accent-secondary"></div>
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-white">Información Básica</h1>
          <button onClick={() => navigate(-1)} className="text-zinc-400 hover:text-white">Volver</button>
        </div>
        
        <form onSubmit={handleSubmit(handleUpdateCourse)} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm text-zinc-400 mb-1">Título</label>
            <input {...register('title')} className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-accent-primary" />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm text-zinc-400 mb-1">Descripción</label>
            <textarea {...register('description')} className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-white h-24 focus:outline-none focus:ring-1 focus:ring-accent-primary" />
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Categoría</label>
            <select {...register('category_id')} className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-accent-primary">
              {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Dificultad</label>
            <select {...register('nivel_dificultad')} className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-accent-primary">
              <option value="PRINCIPIANTE">Principiante</option>
              <option value="INTERMEDIO">Intermedio</option>
              <option value="AVANZADO">Avanzado</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Precio (USD)</label>
            <input type="number" step="0.01" {...register('price')} className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-accent-primary" />
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Duración (Horas)</label>
            <input type="number" {...register('duracion_horas')} className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-accent-primary" />
          </div>
          <div className="md:col-span-2 flex justify-end mt-2">
            <button type="submit" className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition">Guardar Cambios</button>
          </div>
        </form>
      </div>

      {/* Modules & Lessons Section */}
      <div className="bg-background-card border border-zinc-800 rounded-2xl p-8 glass-effect shadow-xl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Contenido del Curso</h2>
          <button 
            onClick={() => setShowModuleForm(!showModuleForm)}
            className="px-4 py-2 bg-accent-primary hover:bg-accent-primary/90 text-white rounded-lg transition font-medium text-sm"
          >
            + Añadir Módulo
          </button>
        </div>

        {showModuleForm && (
          <form onSubmit={handleCreateModule} className="mb-6 p-4 border border-zinc-700 rounded-xl bg-background-dark/50 flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm text-zinc-400 mb-1">Título del Módulo</label>
              <input 
                type="text" 
                value={newModuleTitle} 
                onChange={e => setNewModuleTitle(e.target.value)} 
                className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none" 
                placeholder="Ej. Módulo 1: Introducción"
                required
              />
            </div>
            <button type="submit" className="px-4 py-2 bg-accent-secondary hover:bg-accent-secondary/90 text-white rounded-lg transition">Guardar</button>
            <button type="button" onClick={() => setShowModuleForm(false)} className="px-4 py-2 bg-transparent text-zinc-400 hover:text-white transition">Cancelar</button>
          </form>
        )}

        <div className="space-y-4">
          {course.modules.length === 0 ? (
            <p className="text-zinc-500 text-center py-8">Aún no hay módulos en este curso. ¡Añade uno para empezar!</p>
          ) : (
            course.modules.map((module, mIndex) => (
              <div key={module.id} className="border border-zinc-800 rounded-xl overflow-hidden bg-background-dark">
                <div className="p-4 bg-zinc-800/30 flex justify-between items-center border-b border-zinc-800">
                  <h3 className="font-semibold text-white">Módulo {mIndex + 1}: {module.title}</h3>
                  <div className="flex gap-2">
                    <button onClick={() => setActiveModuleForLesson(module.id)} className="text-sm text-accent-primary hover:text-accent-primary/80">+ Lección</button>
                    <button onClick={() => handleDeleteModule(module.id)} className="text-sm text-red-400 hover:text-red-300 ml-4">Eliminar</button>
                  </div>
                </div>

                <div className="p-4 space-y-3">
                  {module.lessons.map((lesson, lIndex) => (
                    <div key={lesson.id} className="flex justify-between items-center p-3 rounded-lg border border-zinc-800/50 bg-zinc-900/50">
                      <div>
                        <span className="text-sm text-zinc-400 mr-2">{mIndex + 1}.{lIndex + 1}</span>
                        <span className="text-zinc-200">{lesson.title}</span>
                      </div>
                      <button onClick={() => handleDeleteLesson(module.id, lesson.id)} className="text-xs text-red-500/70 hover:text-red-400">Eliminar</button>
                    </div>
                  ))}

                  {module.lessons.length === 0 && activeModuleForLesson !== module.id && (
                    <p className="text-xs text-zinc-500 italic">No hay lecciones en este módulo.</p>
                  )}

                  {activeModuleForLesson === module.id && (
                    <form onSubmit={(e) => handleCreateLesson(e, module.id)} className="p-3 border border-zinc-700 border-dashed rounded-lg bg-zinc-900/80 space-y-3 mt-4">
                      <div>
                        <input 
                          type="text" 
                          value={newLessonTitle} 
                          onChange={e => setNewLessonTitle(e.target.value)} 
                          className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none" 
                          placeholder="Título de la lección"
                          required
                        />
                      </div>
                      <div>
                        <input 
                          type="url" 
                          value={newLessonUrl} 
                          onChange={e => setNewLessonUrl(e.target.value)} 
                          className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none" 
                          placeholder="URL del video (ej. YouTube, Vimeo)"
                          required
                        />
                      </div>
                      <div className="flex justify-end gap-2">
                        <button type="button" onClick={() => setActiveModuleForLesson(null)} className="px-3 py-1 text-xs text-zinc-400 hover:text-white transition">Cancelar</button>
                        <button type="submit" className="px-3 py-1 text-xs bg-accent-primary hover:bg-accent-primary/90 text-white rounded transition">Guardar Lección</button>
                      </div>
                    </form>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default EditCourse;
