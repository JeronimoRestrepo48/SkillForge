"""Vistas del catálogo de cursos."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from core.mixins import InstructorRequiredMixin
from .models import (
    Curso,
    Categoria,
    Modulo,
    Leccion,
    Certificado,
    Calificacion,
    CertificacionIndustria,
    SeccionMaterialCertificacion,
    ExamenCertificacion,
    PreguntaExamen,
    OpcionPregunta,
    AccesoCertificacion,
    DiplomaCertificacionIndustria,
)
from .forms import CursoForm, ModuloForm, LeccionForm, CalificacionForm
from .services import course_service
from .services.rating_service import puede_calificar, obtener_calificacion_curso, obtener_promedio_y_total
from transactions.models import Inscripcion


class CursoListView(LoginRequiredMixin, ListView):
    """Course list (requires authentication)."""
    model = Curso
    template_name = 'catalog/curso_list.html'
    context_object_name = 'cursos'
    paginate_by = 12
    login_url = '/'

    def get_queryset(self):
        cat = self.request.GET.get('categoria')
        return course_service.obtener_cursos_publicados(
            categoria_id=int(cat) if cat and str(cat).isdigit() else None
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        return context


class CursoDetailView(LoginRequiredMixin, DetailView):
    """Course detail (requires authentication)."""
    model = Curso
    template_name = 'catalog/curso_detail.html'
    context_object_name = 'curso'
    login_url = '/'

    def get_queryset(self):
        return course_service.obtener_cursos_publicados().filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['precio_final'] = self.object.calcular_precio_final()
        context['disponible'] = self.object.esta_disponible()
        context['ya_inscrito'] = (
            self.request.user.is_authenticated
            and Inscripcion.objects.filter(
                user=self.request.user, curso=self.object
            ).exclude(estado='CANCELADA').exists()
        )
        rating_info = obtener_promedio_y_total(self.object)
        context['rating_promedio'] = rating_info['promedio']
        context['rating_total'] = rating_info['total']
        context['calificaciones'] = obtener_calificacion_curso(self.object)[:10]
        if self.request.user.is_authenticated:
            context['puede_calificar'] = puede_calificar(self.request.user, self.object)
            mi_cal = Calificacion.objects.filter(
                user=self.request.user, curso=self.object
            ).first()
            context['mi_calificacion'] = mi_cal
            if context['puede_calificar'] or mi_cal:
                context['calificacion_form'] = CalificacionForm(instance=mi_cal)
            else:
                context['calificacion_form'] = None
        else:
            context['puede_calificar'] = False
            context['mi_calificacion'] = None
            context['calificacion_form'] = None
        modulos = course_service.obtener_modulos_de_curso(self.object)
        context['modulos'] = modulos
        context['total_lecciones'] = Leccion.objects.filter(modulo__curso=self.object).count()
        return context


class MisInscripcionesView(LoginRequiredMixin, TemplateView):
    """Student's enrolled courses."""
    template_name = 'catalog/mis_inscripciones.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inscripciones'] = (
            Inscripcion.objects
            .filter(user=self.request.user)
            .exclude(estado='CANCELADA')
            .select_related('curso', 'curso__categoria')
            .order_by('-fecha_inscripcion')
        )
        return context


class CursoAprenderView(LoginRequiredMixin, TemplateView):
    """Course learn view: modules and lessons."""
    template_name = 'catalog/curso_aprender.html'
    login_url = '/'

    def dispatch(self, request, *args, **kwargs):
        curso = get_object_or_404(Curso, pk=kwargs['pk'])
        if not Inscripcion.objects.filter(
            user=request.user, curso=curso
        ).filter(estado__in=('ACTIVA', 'COMPLETADA')).exists():
            return redirect('catalog:course_detail', pk=curso.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso = get_object_or_404(Curso.objects.prefetch_related('modulos__lecciones'), pk=self.kwargs['pk'])
        context['curso'] = curso
        context['modulos'] = course_service.obtener_modulos_de_curso(curso)
        context['progreso'] = course_service.obtener_progreso_curso(self.request.user, curso)
        # Lecciones completadas por el usuario (ids)
        from catalog.models import ProgresoLeccion
        leccion_ids = [l.pk for m in context['modulos'] for l in m.lecciones.all()]
        context['lecciones_completadas'] = set(
            ProgresoLeccion.objects.filter(
                user=self.request.user,
                leccion_id__in=leccion_ids,
                completada=True
            ).values_list('leccion_id', flat=True)
        )
        return context


class LeccionDetailView(LoginRequiredMixin, TemplateView):
    """Vista de una lección individual con navegación siguiente/anterior."""
    template_name = 'catalog/curso_leccion_detail.html'
    login_url = '/'

    def dispatch(self, request, *args, **kwargs):
        curso = get_object_or_404(Curso, pk=kwargs['pk'])
        if not Inscripcion.objects.filter(
            user=request.user, curso=curso
        ).filter(estado__in=('ACTIVA', 'COMPLETADA')).exists():
            return redirect('catalog:course_detail', pk=curso.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso = get_object_or_404(Curso.objects.prefetch_related('modulos__lecciones'), pk=self.kwargs['pk'])
        leccion = get_object_or_404(Leccion, pk=self.kwargs['leccion_pk'], modulo__curso=curso)
        context['curso'] = curso
        context['leccion'] = leccion
        context['modulos'] = course_service.obtener_modulos_de_curso(curso)
        context['progreso'] = course_service.obtener_progreso_curso(self.request.user, curso)
        lecciones_ordenadas = course_service.obtener_lecciones_ordenadas_curso(curso)
        from catalog.models import ProgresoLeccion
        context['lecciones_completadas'] = set(
            ProgresoLeccion.objects.filter(
                user=self.request.user,
                leccion_id__in=[l.pk for l in lecciones_ordenadas],
                completada=True
            ).values_list('leccion_id', flat=True)
        )
        idx = next((i for i, l in enumerate(lecciones_ordenadas) if l.pk == leccion.pk), None)
        context['leccion_anterior'] = lecciones_ordenadas[idx - 1] if idx and idx > 0 else None
        context['leccion_siguiente'] = lecciones_ordenadas[idx + 1] if idx is not None and idx < len(lecciones_ordenadas) - 1 else None
        context['leccion_completada'] = leccion.pk in context['lecciones_completadas']
        return context


class LeccionCompletarView(LoginRequiredMixin, View):
    """Mark lesson complete (POST). At 100% generates certificate."""
    login_url = '/'

    def post(self, request, pk, leccion_pk):
        from django.contrib import messages
        from catalog.services import certificate_service

        curso = get_object_or_404(Curso, pk=pk)
        if not Inscripcion.objects.filter(
            user=request.user, curso=curso
        ).filter(estado__in=('ACTIVA', 'COMPLETADA')).exists():
            return redirect('catalog:course_detail', pk=pk)
        leccion = get_object_or_404(Leccion, pk=leccion_pk, modulo__curso=curso)
        course_service.marcar_leccion_completada(request.user, leccion)
        progreso = course_service.obtener_progreso_curso(request.user, curso)
        if progreso['total'] > 0 and progreso['porcentaje'] >= 100:
            cert = certificate_service.crear_certificado_si_completo(request.user, curso)
            messages.success(
                request,
                'Congratulations! You have completed the course. Your certificate is available in Certifications.'
            )
        else:
            messages.success(request, f'Lesson "{leccion.titulo}" marked as complete.')
        return redirect('catalog:course_learn', pk=pk)


class CursoCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    """Crear curso (solo instructores)."""
    model = Curso
    form_class = CursoForm
    template_name = 'catalog/curso_form.html'
    success_url = reverse_lazy('catalog:my_teaching')

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)


class CursoUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    """Editar curso (solo instructores, solo propios)."""
    model = Curso
    form_class = CursoForm
    template_name = 'catalog/curso_form.html'
    context_object_name = 'curso'
    success_url = reverse_lazy('catalog:my_teaching')

    def get_queryset(self):
        return Curso.objects.filter(instructor=self.request.user)


class CursoDeleteView(LoginRequiredMixin, InstructorRequiredMixin, DeleteView):
    """Eliminar curso (solo instructores, solo propios)."""
    model = Curso
    template_name = 'catalog/curso_confirm_delete.html'
    context_object_name = 'curso'
    success_url = reverse_lazy('catalog:my_teaching')

    def get_queryset(self):
        return Curso.objects.filter(instructor=self.request.user)


class MisCursosView(LoginRequiredMixin, InstructorRequiredMixin, ListView):
    """Listado de cursos del instructor actual."""
    model = Curso
    template_name = 'catalog/mis_cursos.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        return Curso.objects.filter(instructor=self.request.user).order_by('-fecha_creacion')


def _get_curso_instructor(request, curso_pk):
    """Retorna el curso solo si pertenece al instructor actual."""
    return get_object_or_404(Curso, pk=curso_pk, instructor=request.user)


# --- Módulos (instructor) ---


class ModuloListView(LoginRequiredMixin, InstructorRequiredMixin, TemplateView):
    """Listado de módulos de un curso. Solo el instructor del curso."""
    template_name = 'catalog/modulo_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso = _get_curso_instructor(self.request, self.kwargs['curso_pk'])
        context['curso'] = curso
        context['modulos'] = course_service.obtener_modulos_de_curso(curso)
        return context


class ModuloCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    """Crear módulo en un curso."""
    model = Modulo
    form_class = ModuloForm
    template_name = 'catalog/modulo_form.html'
    context_object_name = 'modulo'

    def dispatch(self, request, *args, **kwargs):
        self.curso = _get_curso_instructor(request, kwargs['curso_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curso'] = self.curso
        return context

    def form_valid(self, form):
        form.instance.curso = self.curso
        if form.instance.orden == 0:
            from django.db.models import Max
            agg = self.curso.modulos.aggregate(max_orden=Max('orden'))
            form.instance.orden = (agg['max_orden'] or 0) + 1
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('catalog:module_list', args=[self.curso.pk])


class ModuloUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    """Editar módulo."""
    model = Modulo
    form_class = ModuloForm
    template_name = 'catalog/modulo_form.html'
    context_object_name = 'modulo'

    def get_queryset(self):
        return Modulo.objects.filter(curso__instructor=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curso'] = self.object.curso
        return context

    def get_success_url(self):
        return reverse('catalog:module_list', args=[self.object.curso_id])


class ModuloDeleteView(LoginRequiredMixin, InstructorRequiredMixin, DeleteView):
    """Eliminar módulo."""
    model = Modulo
    template_name = 'catalog/modulo_confirm_delete.html'
    context_object_name = 'modulo'

    def get_queryset(self):
        return Modulo.objects.filter(curso__instructor=self.request.user)

    def get_success_url(self):
        return reverse('catalog:module_list', args=[self.object.curso_id])


# --- Lecciones (instructor) ---


class LeccionListView(LoginRequiredMixin, InstructorRequiredMixin, TemplateView):
    """Listado de lecciones de un módulo."""
    template_name = 'catalog/leccion_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        modulo = get_object_or_404(
            Modulo,
            pk=self.kwargs['modulo_pk'],
            curso__instructor=self.request.user,
        )
        context['modulo'] = modulo
        context['curso'] = modulo.curso
        context['lecciones'] = course_service.obtener_lecciones_de_modulo(modulo)
        return context


class LeccionCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    """Crear lección en un módulo."""
    model = Leccion
    form_class = LeccionForm
    template_name = 'catalog/leccion_form.html'
    context_object_name = 'leccion'

    def dispatch(self, request, *args, **kwargs):
        self.modulo = get_object_or_404(
            Modulo,
            pk=kwargs['modulo_pk'],
            curso__instructor=request.user,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modulo'] = self.modulo
        context['curso'] = self.modulo.curso
        return context

    def form_valid(self, form):
        form.instance.modulo = self.modulo
        if form.instance.orden == 0:
            from django.db.models import Max
            agg = self.modulo.lecciones.aggregate(max_orden=Max('orden'))
            form.instance.orden = (agg['max_orden'] or 0) + 1
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('catalog:lesson_list', args=[self.modulo.curso_id, self.modulo.pk])


class LeccionUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    """Editar lección."""
    model = Leccion
    form_class = LeccionForm
    template_name = 'catalog/leccion_form.html'
    context_object_name = 'leccion'

    def get_queryset(self):
        return Leccion.objects.filter(modulo__curso__instructor=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modulo'] = self.object.modulo
        context['curso'] = self.object.modulo.curso
        return context

    def get_success_url(self):
        return reverse('catalog:lesson_list', args=[self.object.modulo.curso_id, self.object.modulo_id])


class LeccionDeleteView(LoginRequiredMixin, InstructorRequiredMixin, DeleteView):
    """Eliminar lección."""
    model = Leccion
    template_name = 'catalog/leccion_confirm_delete.html'
    context_object_name = 'leccion'

    def get_queryset(self):
        return Leccion.objects.filter(modulo__curso__instructor=self.request.user)

    def get_success_url(self):
        return reverse('catalog:lesson_list', args=[self.object.modulo.curso_id, self.object.modulo_id])


# --- Certificados ---


class MisCertificadosView(LoginRequiredMixin, TemplateView):
    """Certificados de completitud de curso + diplomas de certificaciones de industria."""
    template_name = 'catalog/mis_certificados.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certificados'] = (
            Certificado.objects
            .filter(user=self.request.user)
            .select_related('curso', 'curso__categoria')
            .order_by('-fecha_emision')
        )
        context['diplomas'] = (
            DiplomaCertificacionIndustria.objects
            .filter(user=self.request.user)
            .select_related('certificacion')
            .order_by('-fecha_examen')
        )
        return context


class CertificadoPreviewView(LoginRequiredMixin, TemplateView):
    """Certificate preview (owner only)."""
    template_name = 'catalog/certificado_preview.html'
    login_url = '/'

    def dispatch(self, request, *args, **kwargs):
        self.certificado = get_object_or_404(
            Certificado.objects.select_related('curso', 'user'),
            curso_id=kwargs['curso_pk'],
            user=request.user,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certificado'] = self.certificado
        context['curso'] = self.certificado.curso
        return context


class CertificadoPdfView(LoginRequiredMixin, View):
    """Descarga del certificado en PDF (solo dueño del certificado)."""
    login_url = '/'

    def get(self, request, curso_pk):
        from .services.certificate_service import generar_pdf_certificado
        certificado = get_object_or_404(
            Certificado.objects.select_related('curso', 'user'),
            curso_id=curso_pk,
            user=request.user,
        )
        pdf_bytes = generar_pdf_certificado(certificado)
        filename = f"certificado-{certificado.numero_certificado}.pdf"
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class CertificadoVerificarView(LoginRequiredMixin, TemplateView):
    """Certificate verification by code (requires auth)."""
    login_url = '/'
    template_name = 'catalog/certificado_verificar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        codigo = self.kwargs.get('codigo', '').strip().upper()
        context['codigo'] = codigo
        context['certificado'] = Certificado.objects.filter(
            codigo_verificacion=codigo
        ).select_related('curso', 'user').first()
        return context


# --- Calificaciones ---


class CalificacionCrearActualizarView(LoginRequiredMixin, View):
    """POST: create or update course rating."""
    login_url = '/'

    def post(self, request, curso_pk):
        from django.contrib import messages
        from .services.rating_service import crear_o_actualizar_calificacion

        curso = get_object_or_404(Curso, pk=curso_pk)
        form = CalificacionForm(request.POST)
        if form.is_valid():
            cal, created = crear_o_actualizar_calificacion(
                request.user,
                curso,
                form.cleaned_data['puntuacion'],
                form.cleaned_data.get('comentario', ''),
            )
            if cal:
                messages.success(
                    request,
                    'Tu valoración se ha guardado correctamente.' if created else 'Valoración actualizada.'
                )
            else:
                messages.error(request, 'You can only rate courses you have completed.')
        else:
            messages.error(request, 'Rating must be between 1 and 5.')
        next_url = request.POST.get('next') or reverse('catalog:course_detail', args=[curso_pk])
        return redirect(next_url)


# --- Certificaciones de industria (independientes de cursos; acceso solo con pago) ---


def _tiene_acceso_certificacion(user, certificacion):
    """True si el usuario ha comprado acceso a esta certificación."""
    return AccesoCertificacion.objects.filter(user=user, certificacion=certificacion).exists()


class CertificacionesIndustriaListView(LoginRequiredMixin, ListView):
    """Lista de certificaciones de industria. Acceso al material y examen solo tras pago."""
    model = CertificacionIndustria
    template_name = 'catalog/certificaciones_industria_list.html'
    context_object_name = 'certificaciones'
    login_url = '/'

    def get_queryset(self):
        return CertificacionIndustria.objects.filter(activa=True).order_by('orden', 'nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accesos_slugs'] = set(
            AccesoCertificacion.objects.filter(user=self.request.user).values_list('certificacion__slug', flat=True)
        )
        return context


class CertificacionIndustriaDetailView(LoginRequiredMixin, TemplateView):
    """Detalle de certificación. Si no ha pagado, muestra precio y botón comprar; si ha pagado, material."""
    template_name = 'catalog/certificacion_industria_detail.html'
    login_url = '/'

    def dispatch(self, request, *args, **kwargs):
        self.certificacion = get_object_or_404(
            CertificacionIndustria.objects.prefetch_related('secciones_material'),
            slug=kwargs['slug'],
            activa=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certificacion'] = self.certificacion
        context['puede_acceder'] = _tiene_acceso_certificacion(self.request.user, self.certificacion)
        context['secciones'] = self.certificacion.secciones_material.all().order_by('orden') if context['puede_acceder'] else []
        context['tiene_examen'] = hasattr(self.certificacion, 'examen') and self.certificacion.examen
        return context


class ComprarCertificacionView(LoginRequiredMixin, View):
    """POST: compra de acceso a la certificación (pago simulado). Redirige al detalle."""
    login_url = '/'

    def post(self, request, slug):
        from django.contrib import messages
        certificacion = get_object_or_404(CertificacionIndustria, slug=slug, activa=True)
        if _tiene_acceso_certificacion(request.user, certificacion):
            messages.info(request, 'You already have access to this certification.')
            return redirect('catalog:certificacion_industria_detail', slug=slug)
        AccesoCertificacion.objects.get_or_create(user=request.user, certificacion=certificacion)
        messages.success(request, f'Access to "{certificacion.nombre}" purchased. You can now view the material and take the exam.')
        return redirect('catalog:certificacion_industria_detail', slug=slug)


class ExamenCertificacionView(LoginRequiredMixin, TemplateView):
    """Examen tipo cuestionario (40 preguntas). Solo con acceso comprado. Al aprobar se emite diploma."""
    template_name = 'catalog/examen_certificacion.html'
    login_url = '/'

    def dispatch(self, request, *args, **kwargs):
        self.certificacion = get_object_or_404(
            CertificacionIndustria.objects.all(),
            slug=kwargs['slug'],
            activa=True,
        )
        if not _tiene_acceso_certificacion(request.user, self.certificacion):
            from django.contrib import messages
            messages.warning(request, 'You must purchase access to this certification to take the exam.')
            return redirect('catalog:certificacion_industria_detail', slug=self.certificacion.slug)
        self.examen = getattr(self.certificacion, 'examen', None)
        if not self.examen:
            from django.contrib import messages
            messages.warning(request, 'This certification has no exam available.')
            return redirect('catalog:certificacion_industria_detail', slug=self.certificacion.slug)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certificacion'] = self.certificacion
        context['examen'] = self.examen
        preguntas = self.examen.preguntas.all().order_by('orden').prefetch_related('opciones')
        context['preguntas'] = preguntas
        return context

    def post(self, request, slug):
        from django.contrib import messages
        import random
        import string
        from django.utils import timezone

        examen = self.examen
        preguntas = list(examen.preguntas.all().order_by('orden').prefetch_related('opciones'))
        respuestas = {}
        correctas = 0
        for p in preguntas:
            key = f'pregunta_{p.id}'
            opcion_id = request.POST.get(key)
            if opcion_id:
                try:
                    opcion = OpcionPregunta.objects.get(pk=opcion_id, pregunta=p)
                    respuestas[p.id] = opcion
                    if opcion.es_correcta:
                        correctas += 1
                except OpcionPregunta.DoesNotExist:
                    pass
        total = len(preguntas)
        porcentaje = (correctas * 100 // total) if total else 0
        aprobado = porcentaje >= examen.puntaje_minimo_aprobacion

        diploma = None
        if aprobado:
            diploma, _ = DiplomaCertificacionIndustria.objects.get_or_create(
                user=request.user,
                certificacion=self.certificacion,
                defaults={
                    'puntaje': porcentaje,
                    'aprobado': True,
                    'codigo_verificacion': _generar_codigo_diploma(),
                },
            )
            if not _:
                diploma.puntaje = porcentaje
                diploma.save(update_fields=['puntaje'])

        context = self.get_context_data()
        context['respuestas'] = respuestas
        context['correctas'] = correctas
        context['total'] = total
        context['porcentaje'] = porcentaje
        context['aprobado'] = aprobado
        context['puntaje_minimo'] = examen.puntaje_minimo_aprobacion
        context['diploma'] = diploma
        if aprobado:
            messages.success(request, f'Passed! You got {porcentaje}%. You can download your diploma.')
        else:
            messages.warning(request, f'Not passed: {porcentaje}% (minimum {examen.puntaje_minimo_aprobacion}%).')
        return self.render_to_response(context)


def _generar_codigo_diploma():
    """Genera código único para verificación del diploma."""
    while True:
        code = 'DIP-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        if not DiplomaCertificacionIndustria.objects.filter(codigo_verificacion=code).exists():
            return code


class DiplomaCertificacionPdfView(LoginRequiredMixin, View):
    """Descarga del diploma PDF de certificación de industria (avalación de conocimientos). Solo dueño."""
    login_url = '/'

    def get(self, request, slug):
        from .services.certificate_service import generar_pdf_diploma_industria
        certificacion = get_object_or_404(CertificacionIndustria, slug=slug, activa=True)
        diploma = get_object_or_404(
            DiplomaCertificacionIndustria.objects.select_related('certificacion', 'user'),
            certificacion=certificacion,
            user=request.user,
        )
        pdf_bytes = generar_pdf_diploma_industria(diploma)
        filename = f"diploma-{certificacion.slug}-{request.user.username}.pdf"
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
