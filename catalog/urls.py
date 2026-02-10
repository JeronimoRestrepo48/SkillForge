from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.CursoListView.as_view(), name='course_list'),
    path('verify/<str:codigo>/', views.CertificadoVerificarView.as_view(), name='certificate_verify'),
    path('my-courses/', views.MisInscripcionesView.as_view(), name='my_courses'),
    path('my-certificates/', views.MisCertificadosView.as_view(), name='my_certificates'),
    path('<int:pk>/', views.CursoDetailView.as_view(), name='course_detail'),
    path('<int:pk>/learn/', views.CursoAprenderView.as_view(), name='course_learn'),
    path('<int:pk>/learn/lesson/<int:leccion_pk>/', views.LeccionDetailView.as_view(), name='lesson_detail'),
    path('<int:pk>/learn/lesson/<int:leccion_pk>/complete/', views.LeccionCompletarView.as_view(), name='lesson_complete'),
    path('<int:curso_pk>/certificate/', views.CertificadoPreviewView.as_view(), name='certificate_preview'),
    path('<int:curso_pk>/certificate/pdf/', views.CertificadoPdfView.as_view(), name='certificate_pdf'),
    path('rate/<int:curso_pk>/', views.CalificacionCrearActualizarView.as_view(), name='course_rate'),
    path('create/', views.CursoCreateView.as_view(), name='course_create'),
    path('<int:pk>/edit/', views.CursoUpdateView.as_view(), name='course_update'),
    path('<int:pk>/delete/', views.CursoDeleteView.as_view(), name='course_delete'),
    path('manage/', views.MisCursosView.as_view(), name='my_teaching'),
    path('<int:curso_pk>/modules/', views.ModuloListView.as_view(), name='module_list'),
    path('<int:curso_pk>/modules/create/', views.ModuloCreateView.as_view(), name='module_create'),
    path('<int:curso_pk>/modules/<int:pk>/edit/', views.ModuloUpdateView.as_view(), name='module_update'),
    path('<int:curso_pk>/modules/<int:pk>/delete/', views.ModuloDeleteView.as_view(), name='module_delete'),
    path('<int:curso_pk>/modules/<int:modulo_pk>/lessons/', views.LeccionListView.as_view(), name='lesson_list'),
    path('<int:curso_pk>/modules/<int:modulo_pk>/lessons/create/', views.LeccionCreateView.as_view(), name='lesson_create'),
    path('<int:curso_pk>/modules/<int:modulo_pk>/lessons/<int:pk>/edit/', views.LeccionUpdateView.as_view(), name='lesson_update'),
    path('<int:curso_pk>/modules/<int:modulo_pk>/lessons/<int:pk>/delete/', views.LeccionDeleteView.as_view(), name='lesson_delete'),
    path('certificaciones-industria/', views.CertificacionesIndustriaListView.as_view(), name='certificaciones_industria'),
    path('certificaciones-industria/<slug:slug>/', views.CertificacionIndustriaDetailView.as_view(), name='certificacion_industria_detail'),
    path('certificaciones-industria/<slug:slug>/comprar/', views.ComprarCertificacionView.as_view(), name='comprar_certificacion'),
    path('certificaciones-industria/<slug:slug>/examen/', views.ExamenCertificacionView.as_view(), name='examen_certificacion'),
    path('certificaciones-industria/<slug:slug>/diploma/pdf/', views.DiplomaCertificacionPdfView.as_view(), name='diploma_certificacion_pdf'),
]
