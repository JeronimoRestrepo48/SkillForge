"""
Test all main endpoints for each role (Student, Instructor, Admin).
Ensures home, courses, profile, role-specific pages return 200 where allowed.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Curso, Categoria, Modulo, Leccion
from catalog.models import EstadoCurso
from users.models import TipoUsuario
from transactions.models import Inscripcion

User = get_user_model()


def make_user(username, password, tipo):
    u = User.objects.create_user(username=username, password=password, tipo=tipo)
    return u


class EndpointsStudentTest(TestCase):
    """Endpoints accessible to Student (ESTUDIANTE)."""

    def setUp(self):
        self.client = Client()
        self.user = make_user('student1', 'pass', TipoUsuario.ESTUDIANTE)
        cat = Categoria.objects.create(nombre='Cat', descripcion='D')
        inst = make_user('inst1', 'pass', TipoUsuario.INSTRUCTOR)
        self.curso = Curso.objects.create(
            titulo='C1', descripcion='D1', precio=100, categoria=cat,
            instructor=inst, estado=EstadoCurso.PUBLICADO,
            cupos_totales=10, cupos_disponibles=10
        )

    def test_home_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('core:home'))
        self.assertEqual(r.status_code, 200, msg='Student must access home')

    def test_course_list_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('catalog:course_list'))
        self.assertEqual(r.status_code, 200)

    def test_course_detail_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('catalog:course_detail', args=[self.curso.pk]))
        self.assertEqual(r.status_code, 200)

    def test_my_courses_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('catalog:my_courses'))
        self.assertEqual(r.status_code, 200)

    def test_my_certificates_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('catalog:my_certificates'))
        self.assertEqual(r.status_code, 200)

    def test_cart_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('transactions:cart'))
        self.assertEqual(r.status_code, 200)

    def test_profile_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('users:profile'))
        self.assertEqual(r.status_code, 200)

    def test_my_teaching_denied(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('catalog:my_teaching'))
        self.assertIn(r.status_code, (302, 403), msg='Student must not access my_teaching')

    def test_panel_admin_denied(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('core:panel_admin'))
        self.assertIn(r.status_code, (302, 403))

    def test_checkout_get_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('transactions:checkout'))
        self.assertEqual(r.status_code, 200)

    def test_profile_edit_get_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('users:profile_edit'))
        self.assertEqual(r.status_code, 200)

    def test_course_learn_200_when_enrolled(self):
        Inscripcion.objects.create(user=self.user, curso=self.curso, estado='ACTIVA')
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('catalog:course_learn', args=[self.curso.pk]))
        self.assertEqual(r.status_code, 200)

    def test_logout_redirects_to_login(self):
        self.client.login(username='student1', password='pass')
        r = self.client.post(reverse('core:logout'), follow=False)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.url.endswith('/') or r.url == '/')


class EndpointsInstructorTest(TestCase):
    """Endpoints accessible to Instructor. Includes home (must work)."""

    def setUp(self):
        self.client = Client()
        self.instructor = make_user('instructor1', 'pass', TipoUsuario.INSTRUCTOR)
        cat = Categoria.objects.create(nombre='Cat', descripcion='D')
        self.curso = Curso.objects.create(
            titulo='C1', descripcion='D1', precio=100, categoria=cat,
            instructor=self.instructor, estado=EstadoCurso.PUBLICADO,
            cupos_totales=10, cupos_disponibles=10
        )
        self.modulo = Modulo.objects.create(curso=self.curso, titulo='M1', orden=1)
        self.leccion = Leccion.objects.create(modulo=self.modulo, titulo='L1', tipo='TEXTO', contenido='X', orden=1)

    def test_home_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('core:home'))
        self.assertEqual(r.status_code, 200, msg='Instructor must access home')

    def test_course_list_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('catalog:course_list'))
        self.assertEqual(r.status_code, 200)

    def test_course_detail_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('catalog:course_detail', args=[self.curso.pk]))
        self.assertEqual(r.status_code, 200)

    def test_my_teaching_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('catalog:my_teaching'))
        self.assertEqual(r.status_code, 200)

    def test_course_create_get_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('catalog:course_create'))
        self.assertEqual(r.status_code, 200)

    def test_module_list_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('catalog:module_list', args=[self.curso.pk]))
        self.assertEqual(r.status_code, 200)

    def test_lesson_list_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('catalog:lesson_list', args=[self.curso.pk, self.modulo.pk]))
        self.assertEqual(r.status_code, 200)

    def test_profile_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('users:profile'))
        self.assertEqual(r.status_code, 200)

    def test_cart_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('transactions:cart'))
        self.assertEqual(r.status_code, 200)

    def test_panel_admin_denied(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('core:panel_admin'))
        self.assertIn(r.status_code, (302, 403))

    def test_my_courses_enrolled_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('catalog:my_courses'))
        self.assertEqual(r.status_code, 200)

    def test_profile_edit_get_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('users:profile_edit'))
        self.assertEqual(r.status_code, 200)

    def test_course_edit_get_200(self):
        self.client.login(username='instructor1', password='pass')
        r = self.client.get(reverse('catalog:course_update', args=[self.curso.pk]))
        self.assertEqual(r.status_code, 200)


class EndpointsAdminTest(TestCase):
    """Endpoints accessible to Admin."""

    def setUp(self):
        self.client = Client()
        self.admin = make_user('admin1', 'pass', TipoUsuario.ADMINISTRADOR)
        cat = Categoria.objects.create(nombre='Cat', descripcion='D')
        inst = make_user('inst2', 'pass', TipoUsuario.INSTRUCTOR)
        self.curso = Curso.objects.create(
            titulo='C1', descripcion='D1', precio=100, categoria=cat,
            instructor=inst, estado=EstadoCurso.PUBLICADO,
            cupos_totales=10, cupos_disponibles=10
        )

    def test_home_200(self):
        self.client.login(username='admin1', password='pass')
        r = self.client.get(reverse('core:home'))
        self.assertEqual(r.status_code, 200)

    def test_panel_admin_200(self):
        self.client.login(username='admin1', password='pass')
        r = self.client.get(reverse('core:panel_admin'))
        self.assertEqual(r.status_code, 200)

    def test_course_list_200(self):
        self.client.login(username='admin1', password='pass')
        r = self.client.get(reverse('catalog:course_list'))
        self.assertEqual(r.status_code, 200)

    def test_course_detail_200(self):
        self.client.login(username='admin1', password='pass')
        r = self.client.get(reverse('catalog:course_detail', args=[self.curso.pk]))
        self.assertEqual(r.status_code, 200)

    def test_profile_200(self):
        self.client.login(username='admin1', password='pass')
        r = self.client.get(reverse('users:profile'))
        self.assertEqual(r.status_code, 200)

    def test_profile_edit_get_200(self):
        self.client.login(username='admin1', password='pass')
        r = self.client.get(reverse('users:profile_edit'))
        self.assertEqual(r.status_code, 200)

    def test_health_200_unauthenticated(self):
        r = self.client.get(reverse('core:health'))
        self.assertEqual(r.status_code, 200)
