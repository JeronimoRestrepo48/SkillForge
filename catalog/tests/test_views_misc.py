"""
Tests for catalog views: certificaciones industria, certificate preview/pdf, verify.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import (
    Curso,
    Categoria,
    Modulo,
    Leccion,
    Certificado,
    CertificacionIndustria,
    ExamenCertificacion,
    PreguntaExamen,
    OpcionPregunta,
    AccesoCertificacion,
    DiplomaCertificacionIndustria,
)
from catalog.models import EstadoCurso
from users.models import TipoUsuario
from transactions.models import Inscripcion, EstadoInscripcion

User = get_user_model()


def make_user(username, password, tipo=TipoUsuario.ESTUDIANTE):
    return User.objects.create_user(username=username, password=password, tipo=tipo)


class CertificacionesIndustriaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('student1', 'pass')
        self.cert = CertificacionIndustria.objects.create(
            nombre='Test Industry Cert',
            slug='test-industry-cert',
            descripcion='Test desc',
            precio=Decimal('50'),
            activa=True,
        )

    def test_certificaciones_industria_list_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(reverse('catalog:certificaciones_industria'))
        self.assertEqual(r.status_code, 200)

    def test_certificacion_industria_detail_200(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(
            reverse('catalog:certificacion_industria_detail', args=[self.cert.slug])
        )
        self.assertEqual(r.status_code, 200)


class CertificatePreviewPdfTest(TestCase):
    """Certificate preview and PDF download (owner only)."""

    def setUp(self):
        self.client = Client()
        self.user = make_user('student1', 'pass')
        cat = Categoria.objects.create(nombre='Cat', descripcion='D')
        inst = make_user('inst1', 'pass', TipoUsuario.INSTRUCTOR)
        self.curso = Curso.objects.create(
            titulo='C1',
            descripcion='D1',
            precio=100,
            categoria=cat,
            instructor=inst,
            estado=EstadoCurso.PUBLICADO,
            cupos_totales=10,
            cupos_disponibles=10,
        )
        self.certificado = Certificado.objects.create(
            user=self.user,
            curso=self.curso,
            numero_certificado='SF-CERT-2025-TEST01',
            codigo_verificacion='ABC12345',
        )

    def test_certificate_preview_200_for_owner(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(
            reverse('catalog:certificate_preview', args=[self.curso.pk])
        )
        self.assertEqual(r.status_code, 200)

    def test_certificate_preview_404_for_non_owner(self):
        other = make_user('other1', 'pass')
        self.client.login(username='other1', password='pass')
        r = self.client.get(
            reverse('catalog:certificate_preview', args=[self.curso.pk])
        )
        self.assertEqual(r.status_code, 404)

    def test_certificate_pdf_200_for_owner(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(
            reverse('catalog:certificate_pdf', args=[self.curso.pk])
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get('Content-Type'), 'application/pdf')

    def test_certificate_pdf_404_for_non_owner(self):
        other = make_user('other1', 'pass')
        self.client.login(username='other1', password='pass')
        r = self.client.get(
            reverse('catalog:certificate_pdf', args=[self.curso.pk])
        )
        self.assertEqual(r.status_code, 404)


class CertificateVerifyViewTest(TestCase):
    """Public verification by code."""

    def setUp(self):
        self.client = Client()
        self.user = make_user('student1', 'pass')
        cat = Categoria.objects.create(nombre='Cat', descripcion='D')
        inst = make_user('inst1', 'pass', TipoUsuario.INSTRUCTOR)
        self.curso = Curso.objects.create(
            titulo='C1',
            descripcion='D1',
            precio=100,
            categoria=cat,
            instructor=inst,
            estado=EstadoCurso.PUBLICADO,
            cupos_totales=10,
            cupos_disponibles=10,
        )
        self.certificado = Certificado.objects.create(
            user=self.user,
            curso=self.curso,
            numero_certificado='SF-CERT-2025-VERIFY',
            codigo_verificacion='VERIFY99',
        )

    def test_certificate_verify_200_with_valid_code(self):
        self.client.login(username='student1', password='pass')
        r = self.client.get(
            reverse('catalog:certificate_verify', args=[self.certificado.codigo_verificacion])
        )
        self.assertEqual(r.status_code, 200)
