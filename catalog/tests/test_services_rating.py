"""Tests del servicio de calificaciones."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from catalog.models import Curso, Categoria, Calificacion
from catalog.services.rating_service import (
    puede_calificar,
    crear_o_actualizar_calificacion,
    obtener_promedio_y_total,
)
from transactions.models import Inscripcion, EstadoInscripcion

User = get_user_model()


class RatingServiceTest(TestCase):
    """Tests para rating_service."""

    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='Test', descripcion='Test')
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
            estado='PUBLICADO',
            cupos_totales=10,
            cupos_disponibles=10,
        )

    def test_no_puede_calificar_sin_inscripcion_completada(self):
        """puede_calificar es False si no hay inscripción COMPLETADA."""
        self.assertFalse(puede_calificar(self.estudiante, self.curso))
        Inscripcion.objects.create(
            user=self.estudiante, curso=self.curso, estado=EstadoInscripcion.ACTIVA
        )
        self.assertFalse(puede_calificar(self.estudiante, self.curso))

    def test_puede_calificar_con_inscripcion_completada(self):
        """puede_calificar es True si hay inscripción COMPLETADA."""
        Inscripcion.objects.create(
            user=self.estudiante, curso=self.curso, estado=EstadoInscripcion.COMPLETADA
        )
        self.assertTrue(puede_calificar(self.estudiante, self.curso))

    def test_no_permite_crear_calificacion_sin_inscripcion_completada(self):
        """crear_o_actualizar_calificacion retorna (None, False) sin inscripción completada."""
        cal, created = crear_o_actualizar_calificacion(
            self.estudiante, self.curso, 5, 'Muy bien'
        )
        self.assertIsNone(cal)
        self.assertFalse(created)
        self.assertEqual(Calificacion.objects.filter(curso=self.curso).count(), 0)

    def test_permite_crear_y_actualizar_calificacion_con_inscripcion_completada(self):
        """Con inscripción COMPLETADA se puede crear y actualizar la calificación."""
        Inscripcion.objects.create(
            user=self.estudiante, curso=self.curso, estado=EstadoInscripcion.COMPLETADA
        )
        cal, created = crear_o_actualizar_calificacion(
            self.estudiante, self.curso, 5, 'Excelente'
        )
        self.assertIsNotNone(cal)
        self.assertTrue(created)
        self.assertEqual(cal.puntuacion, 5)
        self.assertEqual(cal.comentario, 'Excelente')
        self.assertTrue(cal.es_verificada)
        cal2, created2 = crear_o_actualizar_calificacion(
            self.estudiante, self.curso, 4, 'Actualizado'
        )
        self.assertIsNotNone(cal2)
        self.assertFalse(created2)
        self.assertEqual(cal2.puntuacion, 4)
        self.assertEqual(cal2.comentario, 'Actualizado')
        self.assertEqual(Calificacion.objects.filter(curso=self.curso).count(), 1)

    def test_obtener_promedio_y_total(self):
        """obtener_promedio_y_total devuelve promedio y total correctos."""
        Inscripcion.objects.create(
            user=self.estudiante, curso=self.curso, estado=EstadoInscripcion.COMPLETADA
        )
        crear_o_actualizar_calificacion(self.estudiante, self.curso, 4, '')
        info = obtener_promedio_y_total(self.curso)
        self.assertEqual(info['promedio'], 4.0)
        self.assertEqual(info['total'], 1)
