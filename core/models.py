"""Core models for SkillForge."""
from django.db import models
from django.conf import settings


class TipoNotificacion(models.TextChoices):
    CERTIFICATE = 'CERTIFICATE', 'Certificate issued'
    BADGE = 'BADGE', 'Badge earned'
    ENROLLMENT = 'ENROLLMENT', 'Enrollment confirmed'
    COURSE_UPDATE = 'COURSE_UPDATE', 'Course updated'
    ORDER = 'ORDER', 'Order update'
    SYSTEM = 'SYSTEM', 'System message'


NOTIFICATION_ICONS = {
    TipoNotificacion.CERTIFICATE: 'bi-award-fill text-warning',
    TipoNotificacion.BADGE: 'bi-stars text-primary',
    TipoNotificacion.ENROLLMENT: 'bi-check-circle-fill text-success',
    TipoNotificacion.COURSE_UPDATE: 'bi-book-fill text-info',
    TipoNotificacion.ORDER: 'bi-box-seam-fill text-secondary',
    TipoNotificacion.SYSTEM: 'bi-bell-fill text-muted',
}


class Notification(models.Model):
    """In-app notification for users."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoNotificacion.choices,
        default=TipoNotificacion.SYSTEM,
    )
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField(blank=True)
    url = models.CharField(max_length=500, blank=True)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['user', '-fecha']),
            models.Index(fields=['user', 'leida']),
        ]

    def __str__(self):
        return f'{self.titulo} → {self.user}'

    @property
    def icon_class(self):
        return NOTIFICATION_ICONS.get(self.tipo, 'bi-bell text-muted')
