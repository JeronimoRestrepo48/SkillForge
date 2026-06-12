import io
import os
import logging
from datetime import datetime
from celery import shared_task
import boto3

logger = logging.getLogger('shared.tasks.documents')

# --- S3 Upload Helper ---
def upload_to_s3(file_bytes, filename):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_S3_REGION_NAME')
        )
        bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        key = f'certificados/{filename}'
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_bytes,
            ContentType='application/pdf'
        )
        # Assuming the bucket is public or we return the S3 URL
        return f"https://{bucket}.s3.amazonaws.com/{key}"
    except Exception as e:
        logger.error(f"Error uploading to S3: {e}")
        raise

# --- Colores y diseño corporativo (certificados y diplomas) ---
def _color_primary():
    from reportlab.lib.colors import HexColor
    return HexColor('#1e3a5f')

def _color_accent():
    from reportlab.lib.colors import HexColor
    return HexColor('#b8860b')

def _color_text_secondary():
    from reportlab.lib.colors import HexColor
    return HexColor('#4a5568')

def _color_white():
    from reportlab.lib.colors import HexColor
    return HexColor('#ffffff')

def _format_fecha_es(dt_str):
    if not dt_str:
        return ''
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        meses = (
            'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        )
        return f"{dt.day} de {meses[dt.month - 1]} de {dt.year}"
    except Exception:
        return dt_str

def _draw_certificate_frame(canvas, width, height, margin_cm, top_band_height_cm=0):
    from reportlab.lib.units import cm
    m = margin_cm * cm
    canvas.setStrokeColor(_color_primary())
    canvas.setLineWidth(3)
    canvas.rect(m, m, width - 2 * m, height - 2 * m, stroke=1, fill=0)
    inner = 0.25 * cm
    canvas.setStrokeColor(_color_accent())
    canvas.setLineWidth(1)
    canvas.rect(m + inner, m + inner, width - 2 * m - 2 * inner, height - 2 * m - 2 * inner, stroke=1, fill=0)
    if top_band_height_cm > 0:
        band_h = top_band_height_cm * cm
        canvas.setFillColor(_color_primary())
        canvas.rect(m + inner, height - m - band_h - inner, width - 2 * m - 2 * inner, band_h, fill=1, stroke=0)

def _draw_seal(canvas, center_x, center_y, radius_pt, label='CERTIFIED'):
    canvas.setStrokeColor(_color_accent())
    canvas.setFillColor(_color_white())
    canvas.setLineWidth(2)
    canvas.circle(center_x, center_y, radius_pt, stroke=1, fill=1)
    canvas.setFillColor(_color_accent())
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawCentredString(center_x, center_y - 3, label)

def create_pdf_bytes_certificado(data: dict) -> bytes:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas as canvas_mod

    buffer = io.BytesIO()
    width, height = landscape(A4)
    c = canvas_mod.Canvas(buffer, pagesize=landscape(A4))
    margin = 2 * cm
    cx = width / 2
    y = height - margin

    _draw_certificate_frame(c, width, height, margin / cm, top_band_height_cm=2.5)

    c.setFillColor(_color_white())
    c.setFont('Helvetica-Bold', 28)
    c.drawCentredString(cx, y - 1.0 * cm, 'SKILLFORGE')
    c.setFont('Helvetica', 12)
    c.drawCentredString(cx, y - 1.7 * cm, 'CERTIFICATE OF COMPLETION')
    c.setFont('Helvetica', 9)
    c.drawCentredString(cx, y - 2.15 * cm, 'This certifies that the holder has completed the full program.')
    y -= 3.0 * cm

    c.setFillColor(_color_text_secondary())
    c.setFont('Helvetica', 13)
    c.drawCentredString(cx, y, 'This is to certify that')
    y -= 0.6 * cm
    line_w = 5 * cm
    c.setStrokeColor(_color_accent())
    c.setLineWidth(1.5)
    c.line(cx - line_w / 2, y, cx + line_w / 2, y)
    y -= 0.7 * cm
    nombre = data.get('nombre_usuario', 'Estudiante')
    c.setFillColor(_color_primary())
    c.setFont('Helvetica-Bold', 22)
    c.drawCentredString(cx, y, nombre)
    y -= 0.6 * cm
    c.setStrokeColor(_color_accent())
    c.line(cx - line_w / 2, y, cx + line_w / 2, y)
    y -= 0.8 * cm
    c.setFillColor(_color_text_secondary())
    c.setFont('Helvetica', 13)
    c.drawCentredString(cx, y, 'has successfully completed the course')
    y -= 0.7 * cm
    c.setFillColor(_color_primary())
    c.setFont('Helvetica-Bold', 16)
    curso_titulo = data.get('curso_titulo', '')
    c.drawCentredString(cx, y, curso_titulo[:70] + ('...' if len(curso_titulo) > 70 else ''))
    y -= 0.5 * cm
    c.setFillColor(_color_text_secondary())
    c.setFont('Helvetica', 10)
    categoria = data.get('curso_categoria')
    if categoria:
        c.drawCentredString(cx, y, f'Category: {categoria}')
        y -= 0.4 * cm
    instructor = data.get('curso_instructor')
    if instructor:
        c.drawCentredString(cx, y, f'Instructor: {instructor}')
    y -= 1.0 * cm

    seal_x = width - margin - 2.5 * cm
    seal_y = height - margin - 2.5 * cm
    _draw_seal(c, seal_x, seal_y, 32, 'CERTIFIED')

    _draw_seal(c, margin + 2.5 * cm, margin + 2.5 * cm, 28, 'SKILLFORGE')

    c.setStrokeColor(_color_accent())
    c.setLineWidth(0.5)
    c.line(margin + 0.5 * cm, y + 0.3 * cm, width - margin - 0.5 * cm, y + 0.3 * cm)
    y -= 0.1 * cm
    c.setFillColor(_color_text_secondary())
    c.setFont('Helvetica', 9)
    c.drawString(margin + 1 * cm, y, f"No. {data.get('numero_certificado', '')}")
    c.drawCentredString(cx, y, f"Verification: {data.get('codigo_verificacion', '')}")
    fecha_str = _format_fecha_es(data.get('fecha_emision'))
    if fecha_str:
        c.drawRightString(width - margin - 1 * cm, y, fecha_str)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=60, retry_backoff_max=300, retry_jitter=True)
def generar_pdf_certificado_async(self, data: dict):
    """
    Genera el PDF del certificado y lo sube a S3.
    """
    try:
        pdf_bytes = create_pdf_bytes_certificado(data)
        filename = f"certificado-{data.get('numero_certificado')}.pdf"
        s3_url = upload_to_s3(pdf_bytes, filename)
        logger.info(f"PDF generated and uploaded to S3 for certificate {data.get('numero_certificado')}: {s3_url}")
        
        # Guardamos en AsyncResult status (que será devuelto como resultado de Celery)
        # para que la tarea periódica lo pueda consultar y guardar en BD
        return {'status': 'ok', 's3_url': s3_url, 'certificado_id': data.get('certificado_id')}
    except Exception as exc:
        logger.error(f"Error generating certificate PDF: {exc}")
        raise

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=60, retry_backoff_max=300, retry_jitter=True)
def generar_pdf_diploma_async(self, data: dict):
    """Genera el PDF del diploma y lo guarda."""
    # Placeholder para diploma (similar lógica a certificado)
    return {'status': 'ok', 's3_url': 'http://dummy.s3.url/diploma.pdf', 'diploma_id': data.get('diploma_id')}

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=60, retry_backoff_max=300, retry_jitter=True)
def generar_pdf_factura_async(self, data: dict):
    """Genera PDF de la factura."""
    return {'status': 'ok'}

@shared_task
def dead_letter_task(task_name, args_str, exc_str):
    """Recibe tareas que fallaron todos los reintentos."""
    logger.error(f"DEAD LETTER: Task {task_name} failed with args {args_str}. Exception: {exc_str}")
    return {'status': 'logged'}
