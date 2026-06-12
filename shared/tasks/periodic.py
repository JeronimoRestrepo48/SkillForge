import logging
import urllib.request
from celery import shared_task

logger = logging.getLogger('shared.tasks.periodic')

@shared_task
def revisar_certificados_pendientes():
    """
    Tarea periódica ejecutada por Celery Beat cada 30 segundos.
    Llama al endpoint interno del certificate-service para que revise
    los estados de AsyncResult de los PDFs en proceso y actualice su BD.
    """
    url = "http://certificate-service:8000/certificates/internal/check-pending-tasks"
    req = urllib.request.Request(url, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = response.read().decode("utf-8")
            logger.info(f"Checked pending certificates: {res_data}")
            return {'status': 'ok'}
    except Exception as exc:
        logger.error(f"Error calling check-pending-tasks: {exc}")
        raise
