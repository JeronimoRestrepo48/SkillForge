"""
Tests for login, register, and unauthenticated access to home.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import TipoUsuario

User = get_user_model()


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            tipo=TipoUsuario.ESTUDIANTE,
        )

    def test_login_get_200(self):
        r = self.client.get(reverse('core:login'))
        self.assertEqual(r.status_code, 200)

    def test_login_post_success_redirects_to_home(self):
        r = self.client.post(
            reverse('core:login'),
            {'username': 'testuser', 'password': 'testpass123'},
            follow=False,
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.url.endswith('/home/') or 'home' in r.url)

    def test_login_post_invalid_returns_200_with_form(self):
        r = self.client.post(
            reverse('core:login'),
            {'username': 'testuser', 'password': 'wrongpassword'},
        )
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.wsgi_request.user.is_authenticated)


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_get_200(self):
        r = self.client.get(reverse('core:register'))
        self.assertEqual(r.status_code, 200)

    def test_register_post_success_creates_user_redirects(self):
        r = self.client.post(
            reverse('core:register'),
            {
                'username': 'newuser',
                'email': 'new@example.com',
                'password1': 'ComplexPass123!',
                'password2': 'ComplexPass123!',
                'tipo': TipoUsuario.ESTUDIANTE,
            },
            follow=False,
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(r.url.endswith('/') or r.url.endswith('/home/') or 'home' in r.url)

    def test_register_post_duplicate_username_returns_200_with_errors(self):
        User.objects.create_user(username='dup', password='p', tipo=TipoUsuario.ESTUDIANTE)
        r = self.client.post(
            reverse('core:register'),
            {
                'username': 'dup',
                'email': 'dup@example.com',
                'password1': 'ComplexPass123!',
                'password2': 'ComplexPass123!',
                'tipo': TipoUsuario.ESTUDIANTE,
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(User.objects.filter(username='dup').count(), 1)


class HomeUnauthenticatedTest(TestCase):
    """Home (landing) requires login."""

    def setUp(self):
        self.client = Client()

    def test_home_redirects_to_login_when_not_authenticated(self):
        r = self.client.get(reverse('core:home'), follow=False)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.url.startswith('/'), msg=f'Redirect URL should start with /: {r.url}')
