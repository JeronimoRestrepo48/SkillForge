"""Tests de mixins de permisos."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminRequiredMixinTest(TestCase):
    """Verifica que AdminRequiredMixin restringe el acceso al panel admin."""

    def setUp(self):
        self.client = Client()

    def test_estudiante_no_accede_panel_admin(self):
        """Estudiante no accede al panel admin (302 o 403)."""
        User.objects.create_user(username='est', password='pass', tipo='ESTUDIANTE')
        self.client.login(username='est', password='pass')
        response = self.client.get(reverse('core:panel_admin'))
        self.assertIn(response.status_code, (302, 403))

    def test_instructor_no_accede_panel_admin(self):
        """Instructor no accede al panel admin (302 o 403)."""
        User.objects.create_user(username='inst', password='pass', tipo='INSTRUCTOR')
        self.client.login(username='inst', password='pass')
        response = self.client.get(reverse('core:panel_admin'))
        self.assertIn(response.status_code, (302, 403))

    def test_administrador_accede_panel_admin(self):
        """Administrador accede al panel (200)."""
        User.objects.create_user(username='admin', password='pass', tipo='ADMINISTRADOR')
        self.client.login(username='admin', password='pass')
        response = self.client.get(reverse('core:panel_admin'))
        self.assertEqual(response.status_code, 200)
