from django.db.models import Count
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from catalog.models import Curso, Categoria, Certificado
from catalog.services import course_service
from core.mixins import AdminRequiredMixin
from transactions.models import Orden, Inscripcion

User = get_user_model()


def _role_flag(user, attr):
    """Return bool from user.attr (handles both callable and property)."""
    val = getattr(user, attr, None)
    if val is None:
        return False
    return val() if callable(val) else bool(val)


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
    """Home: dashboard with stats, progress, and quick links by role."""
    template_name = 'landing.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['site_total_courses'] = Curso.objects.filter(estado='PUBLICADO').count()
        context['site_total_categories'] = Categoria.objects.count()
        if getattr(user, 'tipo', None) == 'ESTUDIANTE' or _role_flag(user, 'es_estudiante'):
            ins = Inscripcion.objects.filter(user=user).exclude(estado='CANCELADA').select_related('curso', 'curso__categoria')
            completed = ins.filter(estado='COMPLETADA').count()
            in_progress = ins.filter(estado='ACTIVA').count()
            context['dashboard_courses_enrolled'] = ins.count()
            context['dashboard_courses_completed'] = completed
            context['dashboard_certificates'] = Certificado.objects.filter(user=user).count()
            progress_list = []
            for i in ins.filter(estado='ACTIVA')[:8]:
                prog = course_service.obtener_progreso_curso(user, i.curso)
                progress_list.append({'curso': i.curso, 'porcentaje': round(prog['porcentaje'], 1), 'completadas': prog['completadas'], 'total': prog['total']})
            context['dashboard_progress'] = progress_list
            context['chart_learning_overview'] = {'completed': completed, 'in_progress': in_progress, 'not_started': max(0, ins.count() - completed - in_progress)}
            context['chart_progress_labels'] = [item['curso'].titulo[:20] + ('…' if len(item['curso'].titulo) > 20 else '') for item in progress_list]
            context['chart_progress_data'] = [item['porcentaje'] for item in progress_list]
            cat_counts = {}
            for i in ins.select_related('curso__categoria'):
                if i.curso.categoria:
                    name = i.curso.categoria.nombre
                    cat_counts[name] = cat_counts.get(name, 0) + 1
            context['chart_categories_labels'] = list(cat_counts.keys())
            context['chart_categories_data'] = list(cat_counts.values())
            context['chart_overall_progress'] = round((sum(p['porcentaje'] for p in progress_list) / len(progress_list)) if progress_list else 0, 1)
        elif getattr(user, 'tipo', None) == 'INSTRUCTOR' or _role_flag(user, 'es_instructor'):
            qs = Curso.objects.filter(instructor=user)
            published = qs.filter(estado='PUBLICADO').count()
            draft = qs.filter(estado='BORRADOR').count()
            context['dashboard_courses_teaching'] = qs.count()
            context['dashboard_courses_published'] = published
            context['chart_course_status'] = {'Published': published, 'Draft': draft}
            cat_counts = dict(qs.values('categoria__nombre').annotate(c=Count('id')).values_list('categoria__nombre', 'c'))
            cat_counts.pop(None, None)
            context['chart_instructor_categories_labels'] = list(cat_counts.keys())
            context['chart_instructor_categories_data'] = list(cat_counts.values())
        elif getattr(user, 'tipo', None) == 'ADMINISTRADOR' or getattr(user, 'is_staff', False):
            context['dashboard_total_users'] = User.objects.count()
            context['dashboard_total_orders'] = Orden.objects.count()
            users_by_type = dict(User.objects.values('tipo').annotate(c=Count('id')).values_list('tipo', 'c'))
            type_display = {'ESTUDIANTE': 'Students', 'INSTRUCTOR': 'Instructors', 'ADMINISTRADOR': 'Admins'}
            context['chart_users_by_type_labels'] = [type_display.get(k, k or 'Other') for k in users_by_type.keys()]
            context['chart_users_by_type_data'] = list(users_by_type.values())
            today = timezone.now().date()
            orders_by_day = []
            for i in range(6, -1, -1):
                d = today - timedelta(days=i)
                orders_by_day.append(Orden.objects.filter(fecha_creacion__date=d).count())
            context['chart_orders_days_labels'] = [(today - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]
            context['chart_orders_days_data'] = orders_by_day
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
