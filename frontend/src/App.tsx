import { RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { router } from './router';

// Inicialización de React Query para manejo del estado de peticiones y caché
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false, // Deshabilitar refetch al cambiar de pestaña
      retry: 1, // Reintentar una vez en caso de error
      staleTime: 5 * 60 * 1000, // 5 minutos de caché antes de considerar obsoletos los datos
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
