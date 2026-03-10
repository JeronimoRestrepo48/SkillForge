"""
Service for creating and managing in-app notifications.
"""
import logging
from core.models import Notification, TipoNotificacion

logger = logging.getLogger('catalog')


def crear_notificacion(user, tipo, titulo, mensaje='', url=''):
    """Creates a notification for the user."""
    return Notification.objects.create(
        user=user, tipo=tipo, titulo=titulo, mensaje=mensaje, url=url,
    )


def notificar_certificado(user, curso):
    crear_notificacion(
        user,
        TipoNotificacion.CERTIFICATE,
        f'Certificate earned: {curso.titulo}',
        'Congratulations! You completed the course and earned a certificate.',
        f'/courses/{curso.pk}/certificate/',
    )


def notificar_badge(user, badge_label):
    crear_notificacion(
        user,
        TipoNotificacion.BADGE,
        f'New badge: {badge_label}',
        f'You earned the "{badge_label}" badge!',
        '/my-account/',
    )


def notificar_inscripcion(user, curso):
    crear_notificacion(
        user,
        TipoNotificacion.ENROLLMENT,
        f'Enrolled in: {curso.titulo}',
        'You can now access the course content.',
        f'/courses/{curso.pk}/learn/',
    )


def notificar_orden(user, numero_orden):
    crear_notificacion(
        user,
        TipoNotificacion.ORDER,
        f'Order confirmed: {numero_orden}',
        'Your purchase has been processed.',
        f'/cart/orders/{numero_orden}/',
    )


def obtener_no_leidas(user):
    return Notification.objects.filter(user=user, leida=False).count()


def obtener_notificaciones(user, limit=30):
    return Notification.objects.filter(user=user)[:limit]


def marcar_todas_leidas(user):
    Notification.objects.filter(user=user, leida=False).update(leida=True)


def marcar_leida(notification_id, user):
    Notification.objects.filter(pk=notification_id, user=user).update(leida=True)
