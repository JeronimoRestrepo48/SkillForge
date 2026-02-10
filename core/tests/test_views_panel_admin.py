"""Tests de vistas del panel de administración."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class PanelAdminViewTest(TestCase):
    """Solo usuarios Administrador o is_staff pueden acceder al panel."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('core:panel_admin')

    def test_acceso_denegado_sin_login(self):
        """Sin autenticación redirige al login (302)."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('core:login')))

    def test_acceso_denegado_estudiante(self):
        """Usuario Estudiante no accede (302 redirect o 403)."""
        user = User.objects.create_user(
            username='est', password='pass', tipo='ESTUDIANTE'
        )
        self.client.login(username='est', password='pass')
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (302, 403))

    def test_acceso_denegado_instructor(self):
        """Usuario Instructor no accede (302 redirect o 403)."""
        user = User.objects.create_user(
            username='inst', password='pass', tipo='INSTRUCTOR'
        )
        self.client.login(username='inst', password='pass')
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (302, 403))

    def test_acceso_ok_administrador(self):
        """Usuario con tipo ADMINISTRADOR accede (200)."""
        user = User.objects.create_user(
            username='admin', password='pass', tipo='ADMINISTRADOR'
        )
        self.client.login(username='admin', password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_acceso_ok_staff(self):
        """Usuario is_staff accede (200) aunque no sea ADMINISTRADOR."""
        user = User.objects.create_user(
            username='staff', password='pass', tipo='ESTUDIANTE', is_staff=True
        )
        self.client.login(username='staff', password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
