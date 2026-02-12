"""
Servicio de certificados - genera certificado al completar 100% del curso
y diplomas de certificación de industria. Incluye generación de PDF con
diseño profesional (bordes, colores, sellos). Generación local con ReportLab.
"""
import io
import random
import string
from django.utils import timezone

from catalog.models import Curso, Certificado
from transactions.models import Inscripcion, EstadoInscripcion


# --- Colores y diseño corporativo (certificados y diplomas) ---
def _color_primary():
    from reportlab.lib.colors import HexColor
    return HexColor('#1e3a5f')  # Azul naval profesional


def _color_accent():
    from reportlab.lib.colors import HexColor
    return HexColor('#b8860b')  # Dorado (DarkGoldenrod)


def _color_text_secondary():
    from reportlab.lib.colors import HexColor
    return HexColor('#4a5568')  # Gris oscuro


def _color_white():
    from reportlab.lib.colors import HexColor
    return HexColor('#ffffff')


def _format_fecha_es(dt):
    """Formato: '15 de marzo de 2025'."""
    if not dt:
        return ''
    meses = (
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    )
    return f"{dt.day} de {meses[dt.month - 1]} de {dt.year}"


def _draw_certificate_frame(canvas, width, height, margin_cm, top_band_height_cm=0):
    """
    Dibuja marco decorativo: borde exterior oscuro, borde interior dorado.
    Si top_band_height_cm > 0, dibuja una banda superior de color primario.
    """
    from reportlab.lib.units import cm
    m = margin_cm * cm
    # Borde exterior (azul naval, grueso)
    canvas.setStrokeColor(_color_primary())
    canvas.setLineWidth(3)
    canvas.rect(m, m, width - 2 * m, height - 2 * m, stroke=1, fill=0)
    # Borde interior (dorado, fino)
    inner = 0.25 * cm
    canvas.setStrokeColor(_color_accent())
    canvas.setLineWidth(1)
    canvas.rect(m + inner, m + inner, width - 2 * m - 2 * inner, height - 2 * m - 2 * inner, stroke=1, fill=0)
    # Banda superior opcional
    if top_band_height_cm > 0:
        band_h = top_band_height_cm * cm
        canvas.setFillColor(_color_primary())
        canvas.rect(m + inner, height - m - band_h - inner, width - 2 * m - 2 * inner, band_h, fill=1, stroke=0)


def _draw_seal(canvas, center_x, center_y, radius_pt, label='CERTIFIED'):
    """Dibuja un sello circular con borde dorado y texto. radius_pt en puntos."""
    canvas.setStrokeColor(_color_accent())
    canvas.setFillColor(_color_white())
    canvas.setLineWidth(2)
    canvas.circle(center_x, center_y, radius_pt, stroke=1, fill=1)
    canvas.setFillColor(_color_accent())
    canvas.setFont('Helvetica-Bold', 8)
    # Texto en una línea (o dos si es largo)
    canvas.drawCentredString(center_x, center_y - 3, label)


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
    Genera el PDF del certificado de completitud de curso con diseño profesional:
    marco decorativo, banda superior, tipografía jerárquica, sello y pie con datos de verificación.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    width, height = A4
    c = canvas.Canvas(buffer, pagesize=A4)
    margin = 1.8 * cm
    cx = width / 2
    y = height - margin

    # --- Marco y banda superior ---
    _draw_certificate_frame(c, width, height, margin / cm, top_band_height_cm=2.2)
    # Contenido de la banda (sobre el rectángulo ya dibujado)
    c.setFillColor(_color_white())
    c.setFont('Helvetica-Bold', 24)
    c.drawCentredString(cx, y - 0.9 * cm, 'SKILLFORGE')
    c.setFont('Helvetica', 11)
    c.drawCentredString(cx, y - 1.5 * cm, 'Certificado de completitud de curso')
    c.setFont('Helvetica', 9)
    c.drawCentredString(cx, y - 1.95 * cm, 'Acredita que el titular ha completado la totalidad del programa.')
    y -= 2.5 * cm

    # --- Cuerpo principal ---
    c.setFillColor(_color_text_secondary())
    c.setFont('Helvetica', 12)
    c.drawCentredString(cx, y, 'Se certifica que')
    y -= 0.5 * cm
    # Línea decorativa
    line_w = 4 * cm
    c.setStrokeColor(_color_accent())
    c.setLineWidth(1.5)
    c.line(cx - line_w / 2, y, cx + line_w / 2, y)
    y -= 0.6 * cm
    nombre = certificado.user.get_full_name() or certificado.user.username
    c.setFillColor(_color_primary())
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(cx, y, nombre)
    y -= 0.5 * cm
    c.setStrokeColor(_color_accent())
    c.line(cx - line_w / 2, y, cx + line_w / 2, y)
    y -= 0.7 * cm
    c.setFillColor(_color_text_secondary())
    c.setFont('Helvetica', 12)
    c.drawCentredString(cx, y, 'ha completado el curso')
    y -= 0.6 * cm
    c.setFillColor(_color_primary())
    c.setFont('Helvetica-Bold', 14)
    # Título del curso puede ser largo; dibujar centrado (una línea)
    curso_titulo = certificado.curso.titulo
    c.drawCentredString(cx, y, curso_titulo[:60] + ('...' if len(curso_titulo) > 60 else ''))
    y -= 1.0 * cm

    # --- Sello (esquina superior derecha) ---
    seal_x = width - margin - 2 * cm
    seal_y = height - margin - 2.2 * cm
    _draw_seal(c, seal_x, seal_y, 28, 'CERTIFIED')

    # --- Pie: número, código de verificación, fecha ---
    c.setStrokeColor(_color_accent())
    c.setLineWidth(0.5)
    c.line(margin + 0.5 * cm, y + 0.3 * cm, width - margin - 0.5 * cm, y + 0.3 * cm)
    y -= 0.1 * cm
    c.setFillColor(_color_text_secondary())
    c.setFont('Helvetica', 9)
    c.drawCentredString(cx, y, f'N.º {certificado.numero_certificado}')
    y -= 0.45 * cm
    c.drawCentredString(cx, y, f'Código de verificación: {certificado.codigo_verificacion}')
    y -= 0.45 * cm
    fecha_str = _format_fecha_es(certificado.fecha_emision)
    if fecha_str:
        c.drawCentredString(cx, y, fecha_str)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def generar_pdf_diploma_industria(diploma) -> bytes:
    """
    Genera el PDF del diploma de certificación de industria (avalación de conocimientos).
    Diseño profesional alineado al certificado de curso: marco, banda, sello y pie.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    width, height = A4
    c = canvas.Canvas(buffer, pagesize=A4)
    margin = 1.8 * cm
    cx = width / 2
    y = height - margin

    # --- Marco y banda superior ---
    _draw_certificate_frame(c, width, height, margin / cm, top_band_height_cm=2.4)
    c.setFillColor(_color_white())
    c.setFont('Helvetica-Bold', 24)
    c.drawCentredString(cx, y - 0.9 * cm, 'SKILLFORGE')
    c.setFont('Helvetica', 11)
    c.drawCentredString(cx, y - 1.5 * cm, 'Certificación profesional avalada por la industria')
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(cx, y - 1.95 * cm, 'DIPLOMA')
    c.setFont('Helvetica', 9)
    c.drawCentredString(cx, y - 2.35 * cm, 'Avalación de conocimientos mediante examen certificado')
    y -= 2.8 * cm

    # --- Cuerpo principal ---
    c.setFillColor(_color_text_secondary())
    c.setFont('Helvetica', 12)
    c.drawCentredString(cx, y, 'Se certifica que')
    y -= 0.5 * cm
    line_w = 4 * cm
    c.setStrokeColor(_color_accent())
    c.setLineWidth(1.5)
    c.line(cx - line_w / 2, y, cx + line_w / 2, y)
    y -= 0.6 * cm
    nombre = diploma.user.get_full_name() or diploma.user.username
    c.setFillColor(_color_primary())
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(cx, y, nombre)
    y -= 0.5 * cm
    c.setStrokeColor(_color_accent())
    c.line(cx - line_w / 2, y, cx + line_w / 2, y)
    y -= 0.7 * cm
    c.setFillColor(_color_text_secondary())
    c.setFont('Helvetica', 12)
    c.drawCentredString(cx, y, 'ha aprobado el examen de la certificación')
    y -= 0.55 * cm
    c.setFillColor(_color_primary())
    c.setFont('Helvetica-Bold', 13)
    cert_nombre = diploma.certificacion.nombre
    c.drawCentredString(cx, y, cert_nombre[:55] + ('...' if len(cert_nombre) > 55 else ''))
    y -= 0.5 * cm
    c.setFillColor(_color_text_secondary())
    c.setFont('Helvetica', 11)
    c.drawCentredString(cx, y, f'con un puntaje de {diploma.puntaje}%')
    y -= 0.9 * cm

    # --- Sello ---
    seal_x = width - margin - 2 * cm
    seal_y = height - margin - 2.4 * cm
    _draw_seal(c, seal_x, seal_y, 28, 'APROBADO')

    # --- Pie ---
    c.setStrokeColor(_color_accent())
    c.setLineWidth(0.5)
    c.line(margin + 0.5 * cm, y + 0.3 * cm, width - margin - 0.5 * cm, y + 0.3 * cm)
    y -= 0.1 * cm
    c.setFillColor(_color_text_secondary())
    c.setFont('Helvetica', 9)
    if diploma.fecha_examen:
        c.drawCentredString(cx, y, _format_fecha_es(diploma.fecha_examen))
        y -= 0.45 * cm
    c.drawCentredString(cx, y, f'Código de verificación: {diploma.codigo_verificacion}')
    y -= 0.6 * cm
    c.setFont('Helvetica', 8)
    c.drawCentredString(cx, y, 'Este diploma acredita la avalación de conocimientos mediante examen.')
    c.drawCentredString(cx, y - 0.35 * cm, 'No equivale a certificado de completitud de curso.')

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
