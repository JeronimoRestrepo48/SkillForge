from django.db.models import Count
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from catalog.services import course_service
from catalog.models import Categoria, Curso
from core.mixins import AdminRequiredMixin
from transactions.models import Orden

User = get_user_model()


# Ensure admin panel requires login first, then admin role
class _AdminRequiredMixin(LoginRequiredMixin, AdminRequiredMixin):
    login_url = '/'


def health_view(request):
    """Endpoint de salud para monitoreo (health check)."""
    return JsonResponse({
        "status": "ok",
        "service": "SkillForge",
        "version": "1.0.0",
    })


class LandingView(LoginRequiredMixin, TemplateView):
    """Home/dashboard after login: featured courses and categories."""
    template_name = 'landing.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cursos_destacados'] = course_service.obtener_cursos_publicados()[:6]
        context['categorias'] = Categoria.objects.all()[:6]
        return context


class PanelAdminView(_AdminRequiredMixin, TemplateView):
    """Panel de administración (solo Administrador o staff)."""
    template_name = 'panel_admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_usuarios'] = User.objects.count()
        context['usuarios_por_tipo'] = dict(
            User.objects.values('tipo').annotate(count=Count('id')).values_list('tipo', 'count')
        )
        context['cursos_publicados'] = Curso.objects.filter(estado='PUBLICADO').count()
        context['ordenes_recientes'] = Orden.objects.select_related('user')[:10]
        return context
