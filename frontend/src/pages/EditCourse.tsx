import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { catalogApi } from '../api/catalog';
import { CourseDetail, Category } from '../types/catalog';
import { useForm } from 'react-hook-form';

export const EditCourse: React.FC = () => {
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
  const [newLessonContentType, setNewLessonContentType] = useState<'VIDEO' | 'QUIZ'>('VIDEO');
  const [newLessonUrl, setNewLessonUrl] = useState('');

  // Quiz Builder States
  const [quizScore, setQuizScore] = useState(70);
  const [quizQuestions, setQuizQuestions] = useState<any[]>([]);

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
        duracion_horas: data.duracion_horas,
        es_certificacion: data.es_certificacion
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
        status: course.status,
        es_certificacion: Boolean(data.es_certificacion)
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

  const handleUpdateModuleFlags = async (moduleId: number, isExam: boolean, isFinal: boolean) => {
    if (!course) return;
    try {
      const mod = course.modules.find(m => m.id === moduleId);
      if (!mod) return;
      await catalogApi.updateModule(course.id, moduleId, {
        title: mod.title,
        sort_order: mod.sort_order,
        es_examen_modulo: isExam,
        es_examen_final: isFinal
      });
      fetchCourseData();
    } catch (err) {
      alert('Error al actualizar módulo');
    }
  };

  const handleCreateLesson = async (e: React.FormEvent, moduleId: number) => {
    e.preventDefault();
    if (!newLessonTitle) return;
    try {
      const module = course?.modules.find(m => m.id === moduleId);
      const sortOrder = module ? module.lessons.length + 1 : 1;
      
      const newLesson = await catalogApi.createLesson(moduleId, {
        title: newLessonTitle,
        content_type: newLessonContentType,
        content: newLessonContentType === 'VIDEO' ? newLessonUrl : 'QUIZ_CONTENT',
        sort_order: sortOrder,
        duration_minutes: 5 // Default for now
      });

      if (newLessonContentType === 'QUIZ') {
        const quizPayload = {
          titulo: `Quiz: ${newLessonTitle}`,
          puntaje_minimo_aprobacion: quizScore,
          questions: quizQuestions.map((q, idx) => ({
            ...q,
            sort_order: idx + 1
          }))
        };
        await catalogApi.createQuiz(newLesson.id, quizPayload);
      }

      setNewLessonTitle('');
      setNewLessonUrl('');
      setNewLessonContentType('VIDEO');
      setQuizQuestions([]);
      setActiveModuleForLesson(null);
      fetchCourseData();
    } catch (err: any) {
      alert('Error al crear lección o quiz');
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

  const addQuizQuestion = () => {
    setQuizQuestions([...quizQuestions, { tipo: 'OPCION_MULTIPLE', enunciado: '', puntaje: 10, options: [] }]);
  };

  const updateQuizQuestion = (index: number, field: string, value: any) => {
    const updated = [...quizQuestions];
    updated[index][field] = value;
    setQuizQuestions(updated);
  };

  const addOption = (qIndex: number) => {
    const updated = [...quizQuestions];
    updated[qIndex].options.push({ texto: '', es_correcta: false });
    setQuizQuestions(updated);
  };

  const updateOption = (qIndex: number, oIndex: number, field: string, value: any) => {
    const updated = [...quizQuestions];
    if (field === 'es_correcta') {
      updated[qIndex].options.forEach((opt: any) => opt.es_correcta = false);
    }
    updated[qIndex].options[oIndex][field] = value;
    setQuizQuestions(updated);
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
          <div className="md:col-span-2 flex items-center gap-3 bg-zinc-900/50 p-4 rounded-xl border border-zinc-800 mt-2">
            <input
              type="checkbox"
              id="es_certificacion"
              {...register('es_certificacion')}
              className="w-5 h-5 accent-primary bg-background-dark border-zinc-700 rounded cursor-pointer"
            />
            <label htmlFor="es_certificacion" className="text-sm font-medium text-white cursor-pointer select-none">
              Este es un curso de certificación
              <span className="block text-xs text-text-secondary mt-1 font-normal">Habilita exámenes por módulo y examen final para emitir el certificado automáticamente.</span>
            </label>
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
                  <div>
                    <h3 className="font-semibold text-white">Módulo {mIndex + 1}: {module.title}</h3>
                    {course.es_certificacion && (
                      <div className="flex items-center gap-4 mt-2">
                        <label className="flex items-center gap-2 text-xs text-zinc-400 hover:text-white cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={module.es_examen_modulo}
                            onChange={(e) => handleUpdateModuleFlags(module.id, e.target.checked, !!module.es_examen_final)}
                            className="accent-primary"
                          />
                          Es examen de módulo
                        </label>
                        <label className="flex items-center gap-2 text-xs text-zinc-400 hover:text-white cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={module.es_examen_final}
                            onChange={(e) => handleUpdateModuleFlags(module.id, !!module.es_examen_modulo, e.target.checked)}
                            className="accent-primary"
                          />
                          Es examen final del curso
                        </label>
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => { setActiveModuleForLesson(module.id); setNewLessonContentType('VIDEO'); }} className="text-sm text-accent-primary hover:text-accent-primary/80">+ Lección</button>
                    <button onClick={() => handleDeleteModule(module.id)} className="text-sm text-red-400 hover:text-red-300 ml-4">Eliminar</button>
                  </div>
                </div>

                <div className="p-4 space-y-3">
                  {module.lessons.map((lesson, lIndex) => (
                    <div key={lesson.id} className="flex justify-between items-center p-3 rounded-lg border border-zinc-800/50 bg-zinc-900/50">
                      <div>
                        <span className="text-sm text-zinc-400 mr-2">{mIndex + 1}.{lIndex + 1}</span>
                        {lesson.content_type === 'QUIZ' && <span className="text-xs px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded mr-2">QUIZ</span>}
                        <span className="text-zinc-200">{lesson.title}</span>
                      </div>
                      <button onClick={() => handleDeleteLesson(module.id, lesson.id)} className="text-xs text-red-500/70 hover:text-red-400">Eliminar</button>
                    </div>
                  ))}

                  {module.lessons.length === 0 && activeModuleForLesson !== module.id && (
                    <p className="text-xs text-zinc-500 italic">No hay lecciones en este módulo.</p>
                  )}

                  {activeModuleForLesson === module.id && (
                    <form onSubmit={(e) => handleCreateLesson(e, module.id)} className="p-5 border border-zinc-700 border-dashed rounded-lg bg-zinc-900/80 space-y-4 mt-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="col-span-2 sm:col-span-1">
                          <label className="block text-xs text-zinc-400 mb-1">Título de la Lección / Quiz</label>
                          <input 
                            type="text" 
                            value={newLessonTitle} 
                            onChange={e => setNewLessonTitle(e.target.value)} 
                            className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none" 
                            required
                          />
                        </div>
                        <div className="col-span-2 sm:col-span-1">
                          <label className="block text-xs text-zinc-400 mb-1">Tipo de contenido</label>
                          <select 
                            value={newLessonContentType}
                            onChange={(e) => setNewLessonContentType(e.target.value as 'VIDEO' | 'QUIZ')}
                            className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none"
                          >
                            <option value="VIDEO">Video</option>
                            <option value="QUIZ">Quiz / Examen</option>
                          </select>
                        </div>
                      </div>

                      {newLessonContentType === 'VIDEO' && (
                        <div>
                          <label className="block text-xs text-zinc-400 mb-1">URL del Video</label>
                          <input 
                            type="url" 
                            value={newLessonUrl} 
                            onChange={e => setNewLessonUrl(e.target.value)} 
                            className="w-full bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none" 
                            placeholder="Ej. YouTube, Vimeo"
                            required
                          />
                        </div>
                      )}

                      {/* Quiz Builder UI */}
                      {newLessonContentType === 'QUIZ' && (
                        <div className="space-y-4 pt-4 border-t border-zinc-800">
                          <div>
                            <label className="block text-xs text-zinc-400 mb-1">Puntaje mínimo de aprobación (%)</label>
                            <input 
                              type="number" 
                              min="0" max="100"
                              value={quizScore} 
                              onChange={e => setQuizScore(Number(e.target.value))} 
                              className="w-32 bg-background-dark border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none" 
                            />
                          </div>

                          <div className="space-y-4">
                            {quizQuestions.map((q, qIndex) => (
                              <div key={qIndex} className="p-4 bg-zinc-800/40 rounded-lg border border-zinc-700 space-y-3">
                                <div className="flex justify-between items-start gap-4">
                                  <div className="flex-1">
                                    <label className="block text-xs text-zinc-400 mb-1">Pregunta {qIndex + 1}</label>
                                    <input 
                                      type="text" 
                                      value={q.enunciado} 
                                      onChange={e => updateQuizQuestion(qIndex, 'enunciado', e.target.value)} 
                                      className="w-full bg-background-dark border border-zinc-600 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none" 
                                      required
                                    />
                                  </div>
                                  <div className="w-32">
                                    <label className="block text-xs text-zinc-400 mb-1">Puntos</label>
                                    <input 
                                      type="number" 
                                      value={q.puntaje} 
                                      onChange={e => updateQuizQuestion(qIndex, 'puntaje', Number(e.target.value))} 
                                      className="w-full bg-background-dark border border-zinc-600 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none" 
                                      required
                                    />
                                  </div>
                                  <div className="w-40">
                                    <label className="block text-xs text-zinc-400 mb-1">Tipo</label>
                                    <select 
                                      value={q.tipo}
                                      onChange={e => updateQuizQuestion(qIndex, 'tipo', e.target.value)}
                                      className="w-full bg-background-dark border border-zinc-600 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none"
                                    >
                                      <option value="OPCION_MULTIPLE">Opción Múltiple</option>
                                      <option value="ABIERTA">Abierta</option>
                                    </select>
                                  </div>
                                  <button type="button" onClick={() => setQuizQuestions(quizQuestions.filter((_, i) => i !== qIndex))} className="mt-6 text-red-400 hover:text-red-300">🗑️</button>
                                </div>

                                {q.tipo === 'OPCION_MULTIPLE' && (
                                  <div className="pl-4 border-l-2 border-zinc-700 space-y-2 mt-2">
                                    {q.options.map((opt: any, oIndex: number) => (
                                      <div key={oIndex} className="flex items-center gap-3">
                                        <input 
                                          type="radio" 
                                          name={`correct_${qIndex}`} 
                                          checked={opt.es_correcta}
                                          onChange={() => updateOption(qIndex, oIndex, 'es_correcta', true)}
                                          className="accent-primary"
                                        />
                                        <input 
                                          type="text" 
                                          value={opt.texto} 
                                          onChange={e => updateOption(qIndex, oIndex, 'texto', e.target.value)} 
                                          className="flex-1 bg-transparent border-b border-zinc-600 px-2 py-1 text-sm text-white focus:outline-none focus:border-primary" 
                                          placeholder="Texto de la opción"
                                          required
                                        />
                                        <button type="button" onClick={() => {
                                          const updated = [...quizQuestions];
                                          updated[qIndex].options.splice(oIndex, 1);
                                          setQuizQuestions(updated);
                                        }} className="text-zinc-500 hover:text-red-400">✖</button>
                                      </div>
                                    ))}
                                    <button type="button" onClick={() => addOption(qIndex)} className="text-xs text-primary mt-2">+ Añadir opción</button>
                                  </div>
                                )}
                              </div>
                            ))}
                            
                            <button type="button" onClick={addQuizQuestion} className="w-full py-2 border border-dashed border-zinc-600 text-zinc-400 hover:text-white rounded-lg text-sm transition">
                              + Añadir Pregunta
                            </button>
                          </div>
                        </div>
                      )}

                      <div className="flex justify-end gap-2 pt-2 border-t border-zinc-800">
                        <button type="button" onClick={() => setActiveModuleForLesson(null)} className="px-4 py-2 text-sm text-zinc-400 hover:text-white transition">Cancelar</button>
                        <button type="submit" className="px-4 py-2 text-sm bg-accent-primary hover:bg-accent-primary/90 text-white rounded transition">Guardar Lección / Quiz</button>
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
