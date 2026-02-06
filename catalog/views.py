"""Vistas del catálogo de cursos."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from core.mixins import InstructorRequiredMixin
from .models import Curso, Categoria
from .forms import CursoForm
from .services import course_service


class CursoListView(ListView):
    """Listado público de cursos publicados."""
    model = Curso
    template_name = 'catalog/curso_list.html'
    context_object_name = 'cursos'
    paginate_by = 12

    def get_queryset(self):
        cat = self.request.GET.get('categoria')
        return course_service.obtener_cursos_publicados(
            categoria_id=int(cat) if cat and str(cat).isdigit() else None
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        return context


class CursoDetailView(DetailView):
    """Detalle de un curso (solo públicos)."""
    model = Curso
    template_name = 'catalog/curso_detail.html'
    context_object_name = 'curso'

    def get_queryset(self):
        return course_service.obtener_cursos_publicados().filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['precio_final'] = self.object.calcular_precio_final()
        context['disponible'] = self.object.esta_disponible()
        return context


class CursoCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    """Crear curso (solo instructores)."""
    model = Curso
    form_class = CursoForm
    template_name = 'catalog/curso_form.html'
    success_url = reverse_lazy('catalog:mis_cursos')

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)


class CursoUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    """Editar curso (solo instructores, solo propios)."""
    model = Curso
    form_class = CursoForm
    template_name = 'catalog/curso_form.html'
    context_object_name = 'curso'
    success_url = reverse_lazy('catalog:mis_cursos')

    def get_queryset(self):
        return Curso.objects.filter(instructor=self.request.user)


class CursoDeleteView(LoginRequiredMixin, InstructorRequiredMixin, DeleteView):
    """Eliminar curso (solo instructores, solo propios)."""
    model = Curso
    template_name = 'catalog/curso_confirm_delete.html'
    context_object_name = 'curso'
    success_url = reverse_lazy('catalog:mis_cursos')

    def get_queryset(self):
        return Curso.objects.filter(instructor=self.request.user)


class MisCursosView(LoginRequiredMixin, InstructorRequiredMixin, ListView):
    """Listado de cursos del instructor actual."""
    model = Curso
    template_name = 'catalog/mis_cursos.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        return Curso.objects.filter(instructor=self.request.user).order_by('-fecha_creacion')
