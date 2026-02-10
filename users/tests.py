"""Tests: public access (login/register only), My account, JWT."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class PublicAccessTest(TestCase):
    """Only login (/) and register are public; rest require auth."""

    def setUp(self):
        self.client = Client()

    def test_login_page_200(self):
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_200(self):
        response = self.client.get(reverse('core:register'))
        self.assertEqual(response.status_code, 200)

    def test_course_list_redirects_to_login_without_auth(self):
        response = self.client.get(reverse('catalog:course_list'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('core:login')) or response.url.startswith('/'))

    def test_course_detail_redirects_to_login_without_auth(self):
        from catalog.models import Curso, Categoria
        from users.models import TipoUsuario
        cat = Categoria.objects.create(nombre='Test', descripcion='Test')
        inst = User.objects.create_user(username='i1', password='p', tipo=TipoUsuario.INSTRUCTOR)
        curso = Curso.objects.create(
            titulo='C', descripcion='D', precio=100, categoria=cat, instructor=inst,
            estado='PUBLICADO', cupos_totales=10, cupos_disponibles=10
        )
        response = self.client.get(reverse('catalog:course_detail', args=[curso.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('core:login')) or response.url.startswith('/'))

    def test_profile_redirects_to_login_without_auth(self):
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('core:login')) or response.url.startswith('/'))

    def test_cart_redirects_to_login_without_auth(self):
        response = self.client.get(reverse('transactions:cart'))
        self.assertEqual(response.status_code, 302)


class MiCuentaTest(TestCase):
    """My account accessible when logged in."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='est', password='test123', tipo='ESTUDIANTE')

    def test_profile_200_when_authenticated(self):
        self.client.login(username='est', password='test123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My account', response.content)
        self.assertIn(b'Certifications', response.content)


class JWTAPITest(TestCase):
    """API JWT: obtener token y GET /api/me/."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='apiuser', password='api123', tipo='ESTUDIANTE')

    def test_token_obtain_returns_access_and_refresh(self):
        response = self.client.post(
            reverse('token_obtain_pair'),
            data={'username': 'apiuser', 'password': 'api123'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)

    def test_api_me_requires_auth(self):
        response = self.client.get(reverse('api_me'))
        self.assertEqual(response.status_code, 401)

    def test_api_me_returns_user_with_jwt(self):
        token_resp = self.client.post(
            reverse('token_obtain_pair'),
            data={'username': 'apiuser', 'password': 'api123'},
            content_type='application/json',
        )
        access = token_resp.json()['access']
        response = self.client.get(
            reverse('api_me'),
            HTTP_AUTHORIZATION=f'Bearer {access}',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['username'], 'apiuser')
        self.assertIn('email', data)
        self.assertIn('tipo', data)
