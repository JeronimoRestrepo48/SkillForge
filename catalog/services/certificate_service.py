"""
Servicio de certificados - genera certificado al completar 100% del curso.
Incluye generación de PDF para descarga (local, sin APIs externas).
"""
import io
import random
import string
from django.utils import timezone

from catalog.models import Curso, Certificado
from transactions.models import Inscripcion, EstadoInscripcion


def _generar_numero_certificado() -> str:
    """Genera número único tipo SF-CERT-2025-XXXXX."""
    year = timezone.now().strftime('%Y')
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'SF-CERT-{year}-{suffix}'


def _generar_codigo_verificacion() -> str:
    """Genera código corto único para verificación pública."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not Certificado.objects.filter(codigo_verificacion=code).exists():
            return code


def crear_certificado_si_completo(user, curso: Curso):
    """
    Crea certificado solo si el progreso del curso es 100% y no existe ya.
    Marca Inscripcion como COMPLETADA si aplica.
    Retorna el Certificado creado o None.
    """
    from catalog.services.course_service import obtener_progreso_curso

    if Certificado.objects.filter(user=user, curso=curso).exists():
        return None

    progreso = obtener_progreso_curso(user, curso)
    if progreso['total'] == 0 or progreso['porcentaje'] < 100:
        return None

    inscripcion = Inscripcion.objects.filter(
        user=user, curso=curso
    ).first()

    if inscripcion and inscripcion.estado != EstadoInscripcion.COMPLETADA:
        inscripcion.estado = EstadoInscripcion.COMPLETADA
        inscripcion.save(update_fields=['estado'])

    numero = _generar_numero_certificado()
    codigo = _generar_codigo_verificacion()
    cert = Certificado.objects.create(
        user=user,
        curso=curso,
        inscripcion=inscripcion,
        numero_certificado=numero,
        codigo_verificacion=codigo,
        plantilla='default',
    )
    # Email simulado: notificación de certificado obtenido
    from django.core.mail import send_mail
    from django.conf import settings
    send_mail(
        subject=f'Has obtenido el certificado - {curso.titulo} - SkillForge',
        message=f'Felicidades. Has completado el curso "{curso.titulo}" y tu certificado ya está disponible en Mis certificados.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
    return cert


def generar_pdf_certificado(certificado: Certificado) -> bytes:
    """
    Genera el PDF del certificado en memoria usando reportlab.
    Retorna los bytes del PDF (generación local, sin APIs externas).
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    width, height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    # Margins
    margin = 2 * cm
    cx = width / 2
    top = height - margin

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(cx, top, "SkillForge")
    top -= 0.6 * cm
    c.setFont("Helvetica", 10)
    c.drawCentredString(cx, top, "Certificado de completitud de curso")
    top -= 0.5 * cm
    c.setFont("Helvetica", 9)
    c.drawCentredString(cx, top, "Acredita que el titular ha completado la totalidad del programa.")
    top -= 1.2 * cm

    c.setFont("Helvetica", 11)
    c.drawCentredString(cx, top, "Se certifica que")
    top -= 0.8 * cm
    nombre = certificado.user.get_full_name() or certificado.user.username
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(cx, top, nombre)
    top -= 0.8 * cm
    c.setFont("Helvetica", 11)
    c.drawCentredString(cx, top, "ha completado el curso")
    top -= 0.8 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(cx, top, certificado.curso.titulo)
    top -= 1.2 * cm

    c.setFont("Helvetica", 9)
    c.drawCentredString(cx, top, f"No. {certificado.numero_certificado}")
    top -= 0.4 * cm
    c.drawCentredString(cx, top, f"Codigo de verificacion: {certificado.codigo_verificacion}")
    top -= 0.4 * cm
    if certificado.fecha_emision:
        meses = ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
                 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre')
        d = certificado.fecha_emision
        fecha_str = f"{d.day} de {meses[d.month - 1]} de {d.year}"
    else:
        fecha_str = ""
    c.drawCentredString(cx, top, fecha_str)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def generar_pdf_diploma_industria(diploma) -> bytes:
    """
    Genera el PDF del diploma de certificación de industria (avalación de conocimientos).
    No es certificado de completitud de curso, sino aval profesional tras aprobar examen.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    width, height = A4
    c = canvas.Canvas(buffer, pagesize=A4)
    margin = 2 * cm
    cx = width / 2
    top = height - margin

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(cx, top, "SkillForge")
    top -= 0.6 * cm
    c.setFont("Helvetica", 10)
    c.drawCentredString(cx, top, "Certificacion profesional avalada por la industria")
    top -= 1 * cm
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(cx, top, "DIPLOMA")
    top -= 0.5 * cm
    c.setFont("Helvetica", 11)
    c.drawCentredString(cx, top, "Avalacion de conocimientos")
    top -= 1 * cm
    c.setFont("Helvetica", 11)
    c.drawCentredString(cx, top, "Se certifica que")
    top -= 0.6 * cm
    nombre = diploma.user.get_full_name() or diploma.user.username
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(cx, top, nombre)
    top -= 0.8 * cm
    c.setFont("Helvetica", 11)
    c.drawCentredString(cx, top, "ha aprobado el examen de la certificacion")
    top -= 0.6 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(cx, top, diploma.certificacion.nombre)
    top -= 0.8 * cm
    c.setFont("Helvetica", 11)
    c.drawCentredString(cx, top, f"con un puntaje de {diploma.puntaje}%")
    top -= 1 * cm
    c.setFont("Helvetica", 9)
    if diploma.fecha_examen:
        meses = ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
                 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre')
        d = diploma.fecha_examen
        fecha_str = f"{d.day} de {meses[d.month - 1]} de {d.year}"
        c.drawCentredString(cx, top, fecha_str)
    top -= 0.5 * cm
    c.drawCentredString(cx, top, f"Codigo de verificacion: {diploma.codigo_verificacion}")
    top -= 0.8 * cm
    c.setFont("Helvetica", 8)
    c.drawCentredString(cx, top, "Este diploma acredita la avalacion de conocimientos mediante examen certificado.")
    c.drawCentredString(cx, top - 0.4 * cm, "No equivale a certificado de completitud de curso.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
