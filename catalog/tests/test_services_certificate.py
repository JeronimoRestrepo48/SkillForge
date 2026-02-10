"""Tests del servicio de certificados."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from catalog.models import Curso, Categoria, Modulo, Leccion, Certificado
from catalog.services.certificate_service import crear_certificado_si_completo
from catalog.services import course_service
from transactions.models import Inscripcion, EstadoInscripcion, Orden

User = get_user_model()


class CertificateServiceTest(TestCase):
    """Tests para crear_certificado_si_completo."""

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
        self.modulo = Modulo.objects.create(curso=self.curso, titulo='M1', orden=0)
        self.leccion1 = Leccion.objects.create(
            modulo=self.modulo, titulo='L1', orden=0
        )
        self.leccion2 = Leccion.objects.create(
            modulo=self.modulo, titulo='L2', orden=1
        )

    def test_no_crea_certificado_si_progreso_no_es_100(self):
        """No se crea certificado si el usuario no ha completado todas las lecciones."""
        Inscripcion.objects.create(
            user=self.estudiante, curso=self.curso, estado=EstadoInscripcion.ACTIVA
        )
        course_service.marcar_leccion_completada(self.estudiante, self.leccion1)
        result = crear_certificado_si_completo(self.estudiante, self.curso)
        self.assertIsNone(result)
        self.assertEqual(Certificado.objects.filter(user=self.estudiante, curso=self.curso).count(), 0)

    def test_crea_certificado_y_marca_inscripcion_completada_cuando_100(self):
        """Al completar el 100% se crea el certificado y la inscripción pasa a COMPLETADA."""
        inscripcion = Inscripcion.objects.create(
            user=self.estudiante, curso=self.curso, estado=EstadoInscripcion.ACTIVA
        )
        course_service.marcar_leccion_completada(self.estudiante, self.leccion1)
        course_service.marcar_leccion_completada(self.estudiante, self.leccion2)
        result = crear_certificado_si_completo(self.estudiante, self.curso)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Certificado)
        self.assertEqual(result.user, self.estudiante)
        self.assertEqual(result.curso, self.curso)
        self.assertTrue(result.numero_certificado.startswith('SF-CERT-'))
        self.assertEqual(len(result.codigo_verificacion), 8)
        inscripcion.refresh_from_db()
        self.assertEqual(inscripcion.estado, EstadoInscripcion.COMPLETADA)

    def test_no_crea_segundo_certificado_si_ya_existe(self):
        """No se crea otro certificado si ya existe uno para ese user/curso."""
        Inscripcion.objects.create(
            user=self.estudiante, curso=self.curso, estado=EstadoInscripcion.COMPLETADA
        )
        course_service.marcar_leccion_completada(self.estudiante, self.leccion1)
        course_service.marcar_leccion_completada(self.estudiante, self.leccion2)
        first = crear_certificado_si_completo(self.estudiante, self.curso)
        self.assertIsNotNone(first)
        second = crear_certificado_si_completo(self.estudiante, self.curso)
        self.assertIsNone(second)
        self.assertEqual(Certificado.objects.filter(user=self.estudiante, curso=self.curso).count(), 1)
