import os
import logging
from celery import Celery
from celery.signals import task_failure
from kombu import Queue, Exchange

logger = logging.getLogger('shared')

_REDIS_URL = os.environ.get('CELERY_BROKER_URL', os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))
_DEFAULT_RESULT_BACKEND = _REDIS_URL.rsplit('/', 1)[0] + '/1' if '/' in _REDIS_URL.rsplit('//', 1)[-1] else 'redis://127.0.0.1:6379/1'
_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', _DEFAULT_RESULT_BACKEND)

app = Celery('skillforge', broker=_REDIS_URL, backend=_RESULT_BACKEND)

app.conf.update(
    accept_content=['json'],
    task_serializer='json',
    result_serializer='json',
    timezone='America/Bogota',  # Default timezone
    task_always_eager=False,
    task_queues=[
        Queue('high_priority', Exchange('high_priority'), routing_key='high_priority'),
        Queue('documents', Exchange('documents'), routing_key='documents'),
        Queue('reports', Exchange('reports'), routing_key='reports'),
        Queue('dead_letter', Exchange('dead_letter'), routing_key='dead_letter'),
    ],
    task_routes={
        'shared.tasks.notifications.enviar_notificacion_orden_async': {'queue': 'high_priority'},
        'shared.tasks.documents.generar_pdf_certificado_async': {'queue': 'documents'},
        'shared.tasks.documents.generar_pdf_diploma_async': {'queue': 'documents'},
        'shared.tasks.documents.generar_pdf_factura_async': {'queue': 'documents'},
        'shared.tasks.documents.dead_letter_task': {'queue': 'dead_letter'},
        'shared.tasks.backups.backup_databases_task': {'queue': 'reports'},
        'shared.tasks.periodic.revisar_certificados_pendientes': {'queue': 'reports'},
    },
    beat_schedule={
        'revisar-certificados-pendientes-cada-30s': {
            'task': 'shared.tasks.periodic.revisar_certificados_pendientes',
            'schedule': 30.0,
        },
        'backup-bases-de-datos-diario': {
            'task': 'shared.tasks.backups.backup_databases_task',
            'schedule': 86400.0,  # Cada día
        }
    }
)

app.autodiscover_tasks(['shared.tasks.documents', 'shared.tasks.notifications', 'shared.tasks.backups', 'shared.tasks.periodic'])

@task_failure.connect
def on_task_failure(sender, task_id, exception, args, kwargs, traceback, einfo, **kw):
    """
    Signal global que captura cualquier tarea que agota todos sus reintentos
    y la encola en dead_letter para auditoría o reintento manual.
    """
    if sender.name == 'shared.tasks.documents.dead_letter_task':
        return

    logger.error(
        "DEAD LETTER: Task %s (id=%s) failed permanently. "
        "Args=%r Exc=%s",
        sender.name, task_id, args, exception,
    )

    try:
        app.send_task(
            'shared.tasks.documents.dead_letter_task',
            args=[sender.name, str(args), str(exception)],
            queue='dead_letter',
            routing_key='dead_letter',
        )
    except Exception as send_exc:
        logger.critical(
            "DEAD LETTER SEND FAILED for task %s: %s", sender.name, send_exc
        )
