from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.MiCuentaView.as_view(), name='profile'),
    path('edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
]
