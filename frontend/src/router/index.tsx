import { createBrowserRouter } from 'react-router-dom';
import Home from '../pages/Home';
import Login from '../pages/Login';
import Register from '../pages/Register';
import CourseCatalog from '../pages/CourseCatalog';
import CourseDetail from '../pages/CourseDetail';
import VideoPlayer from '../pages/VideoPlayer';
import Cart from '../pages/Cart';
import Checkout from '../pages/Checkout';
import PaymentConfirmation from '../pages/PaymentConfirmation';
import StudentDashboard from '../pages/StudentDashboard';
import InstructorDashboard from '../pages/InstructorDashboard';
import CreateCourse from '../pages/CreateCourse';
import EditCourse from '../pages/EditCourse';
import CertificateVerify from '../pages/CertificateVerify';
import ProtectedRoute from '../components/ProtectedRoute';
import Layout from '../components/Layout';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      // Rutas públicas
      {
        path: '',
        element: <Home />,
      },
      {
        path: 'courses',
        element: <CourseCatalog />,
      },
      {
        path: 'courses/:id',
        element: <CourseDetail />,
      },
      {
        path: 'login',
        element: <Login />,
      },
      {
        path: 'register',
        element: <Register />,
      },
      {
        path: 'certificates/:uuid/verify',
        element: <CertificateVerify />,
      },

      // Rutas protegidas (Estudiantes / Usuarios logueados)
      {
        path: 'dashboard',
        element: (
          <ProtectedRoute>
            <StudentDashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: 'courses/:id/learn',
        element: (
          <ProtectedRoute>
            <VideoPlayer />
          </ProtectedRoute>
        ),
      },
      {
        path: 'cart',
        element: (
          <ProtectedRoute>
            <Cart />
          </ProtectedRoute>
        ),
      },
      {
        path: 'checkout',
        element: (
          <ProtectedRoute>
            <Checkout />
          </ProtectedRoute>
        ),
      },
      {
        path: 'payment/confirmation',
        element: (
          <ProtectedRoute>
            <PaymentConfirmation />
          </ProtectedRoute>
        ),
      },

      // Rutas protegidas (Solo Instructores / Administradores)
      {
        path: 'instructor',
        element: (
          <ProtectedRoute allowedRoles={['instructor', 'admin']}>
            <InstructorDashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: 'instructor/courses/new',
        element: (
          <ProtectedRoute allowedRoles={['instructor', 'admin']}>
            <CreateCourse />
          </ProtectedRoute>
        ),
      },
      {
        path: 'instructor/courses/:id/edit',
        element: (
          <ProtectedRoute allowedRoles={['instructor', 'admin']}>
            <EditCourse />
          </ProtectedRoute>
        ),
      },

      // Fallback: Redirigir al Home si la ruta no existe
      {
        path: '*',
        element: <Home />,
      },
    ],
  },
]);
