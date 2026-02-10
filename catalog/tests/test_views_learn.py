"""Tests para vistas de aprendizaje: CursoAprenderView, LeccionDetailView, LeccionCompletarView."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Curso, Categoria, Modulo, Leccion, EstadoCurso
from transactions.models import Inscripcion, EstadoInscripcion

User = get_user_model()


class CursoAprenderViewTest(TestCase):
    """Tests para la vista de índice del curso (course_learn)."""

    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nombre='Cat', descripcion='D')
        self.instructor = User.objects.create_user(
            username='inst', password='pass', tipo='INSTRUCTOR'
        )
        self.estudiante = User.objects.create_user(
            username='est', password='pass', tipo='ESTUDIANTE'
        )
        self.curso = Curso.objects.create(
            titulo='Curso Test',
            descripcion='Desc',
            precio=100,
            categoria=self.categoria,
            instructor=self.instructor,
            estado=EstadoCurso.PUBLICADO,
            cupos_totales=10,
            cupos_disponibles=10,
        )
        Modulo.objects.create(curso=self.curso, titulo='M1', orden=0)

    def test_course_learn_redirects_when_not_enrolled(self):
        """Usuario no inscrito es redirigido al detalle del curso."""
        self.client.login(username='est', password='pass')
        r = self.client.get(reverse('catalog:course_learn', args=[self.curso.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('catalog:course_detail', args=[self.curso.pk]))

    def test_course_learn_200_when_enrolled(self):
        """Usuario inscrito ve la página de aprender."""
        Inscripcion.objects.create(
            user=self.estudiante, curso=self.curso, estado=EstadoInscripcion.ACTIVA
        )
        self.client.login(username='est', password='pass')
        r = self.client.get(reverse('catalog:course_learn', args=[self.curso.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertIn('progreso', r.context)
        self.assertIn('modulos', r.context)
        self.assertIn('lecciones_completadas', r.context)


class LeccionDetailViewTest(TestCase):
    """Tests para la vista de detalle de lección."""

    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nombre='Cat', descripcion='D')
        self.instructor = User.objects.create_user(
            username='inst', password='pass', tipo='INSTRUCTOR'
        )
        self.estudiante = User.objects.create_user(
            username='est', password='pass', tipo='ESTUDIANTE'
        )
        self.curso = Curso.objects.create(
            titulo='Curso Test',
            descripcion='Desc',
            precio=100,
            categoria=self.categoria,
            instructor=self.instructor,
            estado=EstadoCurso.PUBLICADO,
            cupos_totales=10,
            cupos_disponibles=10,
        )
        self.modulo = Modulo.objects.create(curso=self.curso, titulo='M1', orden=0)
        self.leccion = Leccion.objects.create(
            modulo=self.modulo, titulo='L1', tipo='TEXTO', contenido='Contenido', orden=0
        )

    def test_lesson_detail_redirects_when_not_enrolled(self):
        """Usuario no inscrito es redirigido al detalle del curso."""
        self.client.login(username='est', password='pass')
        r = self.client.get(
            reverse('catalog:lesson_detail', args=[self.curso.pk, self.leccion.pk])
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('catalog:course_detail', args=[self.curso.pk]))

    def test_lesson_detail_200_when_enrolled(self):
        """Usuario inscrito ve la lección con anterior/siguiente."""
        Inscripcion.objects.create(
            user=self.estudiante, curso=self.curso, estado=EstadoInscripcion.ACTIVA
        )
        self.client.login(username='est', password='pass')
        r = self.client.get(
            reverse('catalog:lesson_detail', args=[self.curso.pk, self.leccion.pk])
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['leccion'], self.leccion)
        self.assertIn('leccion_anterior', r.context)
        self.assertIn('leccion_siguiente', r.context)


class LeccionCompletarViewTest(TestCase):
    """Tests para marcar lección como completada."""

    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nombre='Cat', descripcion='D')
        self.instructor = User.objects.create_user(
            username='inst', password='pass', tipo='INSTRUCTOR'
        )
        self.estudiante = User.objects.create_user(
            username='est', password='pass', tipo='ESTUDIANTE'
        )
        self.curso = Curso.objects.create(
            titulo='Curso Test',
            descripcion='Desc',
            precio=100,
            categoria=self.categoria,
            instructor=self.instructor,
            estado=EstadoCurso.PUBLICADO,
            cupos_totales=10,
            cupos_disponibles=10,
        )
        self.modulo = Modulo.objects.create(curso=self.curso, titulo='M1', orden=0)
        self.leccion1 = Leccion.objects.create(
            modulo=self.modulo, titulo='L1', tipo='TEXTO', contenido='C1', orden=0
        )
        self.leccion2 = Leccion.objects.create(
            modulo=self.modulo, titulo='L2', tipo='TEXTO', contenido='C2', orden=1
        )

    def test_lesson_complete_redirects_when_not_enrolled(self):
        """POST sin inscripción redirige al detalle del curso."""
        self.client.login(username='est', password='pass')
        r = self.client.post(
            reverse('catalog:lesson_complete', args=[self.curso.pk, self.leccion1.pk])
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('catalog:course_detail', args=[self.curso.pk]))

    def test_lesson_complete_marks_and_redirects(self):
        """POST inscrito marca la lección y redirige a course_learn."""
        Inscripcion.objects.create(
            user=self.estudiante, curso=self.curso, estado=EstadoInscripcion.ACTIVA
        )
        self.client.login(username='est', password='pass')
        r = self.client.post(
            reverse('catalog:lesson_complete', args=[self.curso.pk, self.leccion1.pk]),
            follow=True
        )
        self.assertEqual(r.status_code, 200)
        self.assertRedirects(
            r,
            reverse('catalog:course_learn', args=[self.curso.pk]),
            status_code=302,
            target_status_code=200,
        )
        from catalog.models import ProgresoLeccion
        self.assertTrue(
            ProgresoLeccion.objects.filter(
                user=self.estudiante, leccion=self.leccion1, completada=True
            ).exists()
        )

    def test_lesson_complete_at_100_shows_certificate_message(self):
        """Al completar la última lección se muestra mensaje de certificado."""
        Inscripcion.objects.create(
            user=self.estudiante, curso=self.curso, estado=EstadoInscripcion.ACTIVA
        )
        self.client.login(username='est', password='pass')
        self.client.post(
            reverse('catalog:lesson_complete', args=[self.curso.pk, self.leccion1.pk])
        )
        r = self.client.post(
            reverse('catalog:lesson_complete', args=[self.curso.pk, self.leccion2.pk]),
            follow=True
        )
        self.assertEqual(r.status_code, 200)
        messages = list(r.context.get('messages', []))
        message_texts = [str(m) for m in messages]
        self.assertTrue(
            any('completado el curso' in t or 'certificado' in t for t in message_texts),
            f'Expected certificate message in: {message_texts}'
        )
