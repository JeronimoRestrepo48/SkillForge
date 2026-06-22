import React from 'react';
import { createBrowserRouter } from 'react-router-dom';
import Home from '../pages/Home';
import ProtectedRoute from '../components/ProtectedRoute';
import Layout from '../components/Layout';

// Lazy loaded page components
const Login = React.lazy(() => import('../pages/Login'));
const Register = React.lazy(() => import('../pages/Register'));
const CourseCatalog = React.lazy(() => import('../pages/CourseCatalog'));
const CourseDetail = React.lazy(() => import('../pages/CourseDetail'));
const VideoPlayer = React.lazy(() => import('../pages/VideoPlayer'));
const Cart = React.lazy(() => import('../pages/Cart'));
const Checkout = React.lazy(() => import('../pages/Checkout'));
const PaymentConfirmation = React.lazy(() => import('../pages/PaymentConfirmation'));
const StudentDashboard = React.lazy(() => import('../pages/StudentDashboard'));
const InstructorDashboard = React.lazy(() => import('../pages/InstructorDashboard'));
const CreateCourse = React.lazy(() => import('../pages/CreateCourse'));
const EditCourse = React.lazy(() => import('../pages/EditCourse'));
const CertificateVerify = React.lazy(() => import('../pages/CertificateVerify'));
const InstructorProfile = React.lazy(() => import('../pages/InstructorProfile'));
const EditInstructorProfile = React.lazy(() => import('../pages/EditInstructorProfile'));
const Trayectorias = React.lazy(() => import('../pages/Trayectorias'));
const TrayectoriaDetail = React.lazy(() => import('../pages/TrayectoriaDetail'));
const AdminTrayectorias = React.lazy(() => import('../pages/AdminTrayectorias'));
const QuizPlayer = React.lazy(() => import('../pages/QuizPlayer'));

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
      {
        path: 'instructors/:userId',
        element: <InstructorProfile />,
      },
      {
        path: 'trayectorias',
        element: <Trayectorias />,
      },
      {
        path: 'trayectorias/:id',
        element: <TrayectoriaDetail />,
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
        path: 'courses/:courseId/lessons/:lessonId/quiz',
        element: (
          <ProtectedRoute>
            <QuizPlayer />
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
      {
        path: 'instructor/profile/edit',
        element: (
          <ProtectedRoute allowedRoles={['instructor', 'admin']}>
            <EditInstructorProfile />
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/trayectorias',
        element: (
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminTrayectorias />
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
