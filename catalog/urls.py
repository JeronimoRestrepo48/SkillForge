from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.CursoListView.as_view(), name='curso_list'),
    path('<int:pk>/', views.CursoDetailView.as_view(), name='curso_detail'),
    path('crear/', views.CursoCreateView.as_view(), name='curso_create'),
    path('<int:pk>/editar/', views.CursoUpdateView.as_view(), name='curso_update'),
    path('<int:pk>/eliminar/', views.CursoDeleteView.as_view(), name='curso_delete'),
    path('mis-cursos/', views.MisCursosView.as_view(), name='mis_cursos'),
]
