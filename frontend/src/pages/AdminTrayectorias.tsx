import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';
import { Trayectoria, Course } from '../types/catalog';

export const AdminTrayectorias: React.FC = () => {
  const queryClient = useQueryClient();
  
  // Create / Edit form states
  const [nombre, setNombre] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [categoria, setCategoria] = useState('');

  // Course addition states
  const [selectedCourseId, setSelectedCourseId] = useState('');
  const [sortOrder, setSortOrder] = useState('1');

  const { data: trayectorias, isLoading } = useQuery<Trayectoria[]>({
    queryKey: ['trayectorias'],
    queryFn: () => catalogApi.getTrayectorias(),
  });

  const { data: coursesData } = useQuery({
    queryKey: ['courses'],
    queryFn: () => catalogApi.getCourses({ page_size: 100 }), // Get many courses for the dropdown
  });

  const createMutation = useMutation({
    mutationFn: () => catalogApi.createTrayectoria({ nombre, descripcion, categoria_general: categoria }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trayectorias'] });
      resetForm();
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => catalogApi.deleteTrayectoria(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['trayectorias'] })
  });

  const addCourseMutation = useMutation({
    mutationFn: ({ tId, cId, order }: { tId: number, cId: number, order: number }) => 
      catalogApi.addCourseToTrayectoria(tId, { course_id: cId, sort_order: order }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['trayectorias'] })
  });

  const removeCourseMutation = useMutation({
    mutationFn: ({ tId, cId }: { tId: number, cId: number }) => 
      catalogApi.removeCourseFromTrayectoria(tId, cId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['trayectorias'] })
  });

  const resetForm = () => {
    setNombre('');
    setDescripcion('');
    setCategoria('');
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate();
  };

  if (isLoading) return <div className="text-center mt-12">Cargando...</div>;

  return (
    <div className="max-w-6xl mx-auto mt-8 mb-16 px-4">
      <h1 className="text-3xl font-bold text-white mb-8">Administrar Trayectorias</h1>

      {/* Formulario Crear */}
      <div className="bg-[#111111] p-6 rounded-2xl border border-zinc-800 mb-8">
        <h2 className="text-xl font-bold text-white mb-4">Crear Nueva Trayectoria</h2>
        <form onSubmit={handleCreateSubmit} className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm text-text-secondary mb-1">Nombre</label>
            <input value={nombre} onChange={e => setNombre(e.target.value)} required className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 rounded-lg text-white" />
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm text-text-secondary mb-1">Categoría General</label>
            <input value={categoria} onChange={e => setCategoria(e.target.value)} className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 rounded-lg text-white" />
          </div>
          <div className="w-full">
            <label className="block text-sm text-text-secondary mb-1">Descripción</label>
            <textarea value={descripcion} onChange={e => setDescripcion(e.target.value)} className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 rounded-lg text-white" rows={2} />
          </div>
          <button type="submit" disabled={createMutation.isPending} className="px-6 py-2 bg-primary text-white font-bold rounded-lg hover:bg-primary-dark">
            Guardar
          </button>
        </form>
      </div>

      {/* Lista de Trayectorias */}
      <div className="space-y-6">
        {trayectorias?.map(t => (
          <div key={t.id} className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-2xl font-bold text-white">{t.nombre}</h3>
                <p className="text-text-secondary">{t.descripcion}</p>
              </div>
              <button onClick={() => deleteMutation.mutate(t.id)} className="text-red-500 hover:text-red-400 font-bold text-sm">Eliminar</button>
            </div>

            <div className="bg-zinc-950 p-4 rounded-xl border border-zinc-800">
              <h4 className="text-sm font-bold text-white mb-3">Cursos en la trayectoria:</h4>
              <ul className="space-y-2 mb-4">
                {t.cursos?.sort((a, b) => a.sort_order - b.sort_order).map(tc => (
                  <li key={tc.course_id} className="flex justify-between items-center bg-zinc-900 px-3 py-2 rounded-lg text-sm">
                    <span className="text-white">
                      <span className="text-primary mr-2">#{tc.sort_order}</span>
                      {tc.course?.title || `Curso ID: ${tc.course_id}`}
                    </span>
                    <button onClick={() => removeCourseMutation.mutate({ tId: t.id, cId: tc.course_id })} className="text-red-500 text-xs hover:underline">Quitar</button>
                  </li>
                ))}
                {(!t.cursos || t.cursos.length === 0) && <li className="text-xs text-text-muted">No hay cursos asignados.</li>}
              </ul>

              <div className="flex gap-2 items-end border-t border-zinc-800 pt-4 mt-2">
                <div className="flex-1">
                  <select value={selectedCourseId} onChange={e => setSelectedCourseId(e.target.value)} className="w-full px-2 py-1.5 bg-zinc-800 border border-zinc-700 rounded text-sm text-white">
                    <option value="">Seleccionar curso...</option>
                    {coursesData?.results.map((c: Course) => (
                      <option key={c.id} value={c.id}>{c.title}</option>
                    ))}
                  </select>
                </div>
                <div className="w-20">
                  <input type="number" placeholder="Orden" value={sortOrder} onChange={e => setSortOrder(e.target.value)} className="w-full px-2 py-1.5 bg-zinc-800 border border-zinc-700 rounded text-sm text-white" />
                </div>
                <button 
                  onClick={() => selectedCourseId && addCourseMutation.mutate({ tId: t.id, cId: Number(selectedCourseId), order: Number(sortOrder) })}
                  className="px-4 py-1.5 bg-zinc-700 hover:bg-zinc-600 text-white text-sm rounded"
                >
                  Agregar
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdminTrayectorias;
