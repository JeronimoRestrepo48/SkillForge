"""Catalog REST API list pagination."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Categoria, Curso, EstadoCurso
from users.models import TipoUsuario

User = get_user_model()


class CatalogAPIPaginationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='api_student', password='secret', tipo=TipoUsuario.ESTUDIANTE)
        self.cat = Categoria.objects.create(nombre='Cat', descripcion='')
        inst = User.objects.create_user(username='api_inst', password='secret', tipo=TipoUsuario.INSTRUCTOR)
        for i in range(25):
            Curso.objects.create(
                titulo=f'API Course {i}',
                descripcion='Desc',
                precio=Decimal('10'),
                categoria=self.cat,
                instructor=inst,
                estado=EstadoCurso.PUBLICADO,
                cupos_totales=5,
                cupos_disponibles=5,
            )

    def test_courses_list_is_paginated(self):
        self.client.login(username='api_student', password='secret')
        r = self.client.get(reverse('api_course_list'))
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('results', data)
        self.assertEqual(data['count'], 25)
        self.assertEqual(len(data['results']), 20)
        self.assertIsNotNone(data.get('next'))

    def test_categories_list_supports_pagination_shape(self):
        self.client.login(username='api_student', password='secret')
        r = self.client.get(reverse('api_category_list'))
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('results', data)
        self.assertGreaterEqual(data['count'], 1)
