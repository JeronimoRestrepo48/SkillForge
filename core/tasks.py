"""
Tareas asíncronas (Celery + Redis): notificaciones y reportes en segundo plano.
"""
import logging

from celery import shared_task
from django.contrib.auth import get_user_model

logger = logging.getLogger('catalog')

User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def enviar_notificacion_orden_async(self, user_id: int, numero_orden: str):
    """Crea notificación in-app tras confirmar una orden (proceso en background)."""
    from core.services import notification_service

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning('enviar_notificacion_orden_async: user %s not found', user_id)
        return {'status': 'skipped', 'reason': 'user_not_found'}

    notification_service.notificar_orden(user, numero_orden)
    logger.info('Async order notification created for user=%s order=%s', user_id, numero_orden)
    return {'status': 'ok', 'user_id': user_id, 'order': numero_orden}


@shared_task(bind=True, max_retries=3, default_retry_delay=15)
def generar_reporte_actividad_async(self, user_id: int):
    """
    Genera un reporte resumido de actividad del usuario (inscripciones, órdenes).
    Persiste el resultado como notificación para evidenciar el broker.
    """
    from core.models import Notification, TipoNotificacion
    from transactions.models import Orden, Inscripcion

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return {'status': 'skipped', 'reason': 'user_not_found'}

    inscripciones = Inscripcion.objects.filter(user=user).exclude(estado='CANCELADA').count()
    ordenes = Orden.objects.filter(user=user).count()
    mensaje = (
        f'Enrollments: {inscripciones}, Orders: {ordenes}. '
        'Generated asynchronously via Celery/Redis.'
    )
    Notification.objects.create(
        user=user,
        tipo=TipoNotificacion.ORDER,
        titulo='Activity report ready',
        mensaje=mensaje,
        url='/notifications/',
    )
    logger.info('Activity report generated for user=%s', user_id)
    return {'status': 'ok', 'enrollments': inscripciones, 'orders': ordenes}
