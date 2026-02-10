from django.urls import path
from users.views import LoginView, RegisterView, LogoutView
from . import views

app_name = 'core'

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('home/', views.LandingView.as_view(), name='home'),
    path('health/', views.health_view, name='health'),
    path('panel/', views.PanelAdminView.as_view(), name='panel_admin'),
]
