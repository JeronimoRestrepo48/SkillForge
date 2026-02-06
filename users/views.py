from django.contrib.auth import login
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegisterForm
from .services import user_service


class RegisterView(CreateView):
    """Vista de registro de usuarios."""
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('core:landing')

    def form_valid(self, form):
        tipo = form.cleaned_data['tipo']
        user = user_service.crear_usuario(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
            first_name=form.cleaned_data.get('first_name', ''),
            last_name=form.cleaned_data.get('last_name', ''),
            tipo=tipo,
        )
        login(self.request, user)
        messages.success(self.request, f'¡Bienvenido a SkillForge! Cuenta creada como {user.get_tipo_display}.')
        return redirect(self.success_url)


class LoginView(BaseLoginView):
    """Vista de inicio de sesión."""
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class LogoutView(BaseLogoutView):
    """Vista de cierre de sesión."""
    next_page = 'core:landing'
