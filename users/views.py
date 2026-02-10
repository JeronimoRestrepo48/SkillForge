from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, UpdateView
from .forms import RegisterForm, ProfileForm
from .models import User, UserProfile
from .services import user_service


class RegisterView(CreateView):
    """Vista de registro de usuarios."""
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('core:home')

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

    def get_success_url(self):
        """Redirect by role after login."""
        user = self.request.user
        if user.tipo == 'ADMINISTRADOR' or user.is_staff:
            return reverse('core:panel_admin')
        if user.tipo == 'INSTRUCTOR':
            return reverse('catalog:my_teaching')
        return reverse('core:home')


class LogoutView(BaseLogoutView):
    """Vista de cierre de sesión. Redirige al login (/) tras cerrar sesión."""
    next_page = '/'
    # Permitir POST (formulario del navbar) y GET
    http_method_names = ['get', 'post', 'head', 'options']


class MiCuentaView(LoginRequiredMixin, TemplateView):
    """My account: Profile, My courses, Certifications, Cart tabs."""
    template_name = 'users/mi_cuenta.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from transactions.models import Inscripcion
        from transactions.services import obtener_o_crear_carrito
        from catalog.models import Certificado
        context['inscripciones'] = (
            Inscripcion.objects
            .filter(user=self.request.user)
            .exclude(estado='CANCELADA')
            .select_related('curso', 'curso__categoria')
            .order_by('-fecha_inscripcion')[:20]
        )
        context['certificados'] = (
            Certificado.objects
            .filter(user=self.request.user)
            .select_related('curso')
            .order_by('-fecha_emision')
        )
        carrito = obtener_o_crear_carrito(self.request.user)
        context['carrito'] = carrito
        context['carrito_items'] = carrito.items.select_related('curso').all()
        context['profile_form'] = ProfileForm(instance=self.request.user)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update profile (name, email, bio)."""
    model = User
    form_class = ProfileForm
    template_name = 'users/profile_edit.html'
    login_url = '/'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        bio = form.cleaned_data.pop('bio', '')
        response = super().form_valid(form)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user, defaults={'bio': bio})
        profile.bio = bio
        profile.save()
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return response
