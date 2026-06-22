import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authApi } from '../api/auth';
import { useAuth } from '../context/AuthContext';
import { useForm as useHookForm } from 'react-hook-form';

interface ProfileFormData {
  bio: string;
  carrera: string;
  estudios: string;
  linkedin_url: string;
  sitio_web: string;
  avatar_url: string;
}

export const EditInstructorProfile: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { register, handleSubmit, setValue } = useHookForm<ProfileFormData>();

  const { data: profile, isLoading } = useQuery({
    queryKey: ['instructorProfile', user?.id],
    queryFn: () => authApi.getInstructorProfile(user!.id),
    enabled: !!user,
    retry: false,
  });

  useEffect(() => {
    if (profile) {
      setValue('bio', profile.bio || '');
      setValue('carrera', profile.carrera || '');
      setValue('estudios', profile.estudios || '');
      setValue('linkedin_url', profile.linkedin_url || '');
      setValue('sitio_web', profile.sitio_web || '');
      setValue('avatar_url', profile.avatar_url || '');
    }
  }, [profile, setValue]);

  const updateMutation = useMutation({
    mutationFn: (data: ProfileFormData) => authApi.updateInstructorProfile(user!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instructorProfile', user?.id] });
      alert('Perfil actualizado con éxito');
      navigate(`/instructors/${user?.id}`);
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'Error al actualizar el perfil');
    }
  });

  const onSubmit = (data: ProfileFormData) => {
    updateMutation.mutate(data);
  };

  if (isLoading) {
    return <div className="text-center mt-12 text-text-secondary">Cargando perfil...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto mt-8 mb-16 p-8 bg-[#111111] rounded-3xl border border-zinc-800 shadow-2xl glass-effect">
      <h2 className="text-2xl font-bold text-white mb-6">Editar Perfil de Instructor</h2>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-text-secondary mb-1">Carrera / Título Corto</label>
          <input
            {...register('carrera', { maxLength: 200 })}
            className="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-xl text-white focus:outline-none focus:border-primary transition"
            placeholder="Ej: Ingeniero de Software, Data Scientist..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-text-secondary mb-1">Biografía</label>
          <textarea
            {...register('bio')}
            rows={4}
            className="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-xl text-white focus:outline-none focus:border-primary transition"
            placeholder="Cuéntale a los estudiantes sobre ti..."
          ></textarea>
        </div>

        <div>
          <label className="block text-sm font-medium text-text-secondary mb-1">Formación y Estudios</label>
          <textarea
            {...register('estudios')}
            rows={3}
            className="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-xl text-white focus:outline-none focus:border-primary transition"
            placeholder="Tus títulos, certificaciones, etc."
          ></textarea>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">LinkedIn URL</label>
            <input
              {...register('linkedin_url')}
              className="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-xl text-white focus:outline-none focus:border-primary transition"
              placeholder="https://linkedin.com/in/..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Sitio Web Personal</label>
            <input
              {...register('sitio_web')}
              className="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-xl text-white focus:outline-none focus:border-primary transition"
              placeholder="https://tusitio.com"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-text-secondary mb-1">URL del Avatar</label>
          <input
            {...register('avatar_url')}
            className="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-xl text-white focus:outline-none focus:border-primary transition"
            placeholder="https://..."
          />
        </div>

        <div className="pt-4 flex gap-4">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="px-6 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-xl font-semibold transition"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="px-6 py-2 bg-primary hover:bg-primary-dark text-white rounded-xl font-semibold transition disabled:opacity-50"
          >
            {updateMutation.isPending ? 'Guardando...' : 'Guardar Perfil'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditInstructorProfile;
