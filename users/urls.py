from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('registro/', views.RegisterView.as_view(), name='register'),
    path('iniciar-sesion/', views.LoginView.as_view(), name='login'),
    path('cerrar-sesion/', views.LogoutView.as_view(), name='logout'),
]
