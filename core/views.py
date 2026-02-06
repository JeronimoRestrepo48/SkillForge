from django.views.generic import TemplateView
from catalog.services import course_service
from catalog.models import Categoria


class LandingView(TemplateView):
    """Vista de la página principal con cursos destacados."""
    template_name = 'landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cursos_destacados'] = course_service.obtener_cursos_publicados()[:6]
        context['categorias'] = Categoria.objects.all()[:6]
        return context
