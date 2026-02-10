"""
Configuración específica para desarrollo.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

# Email simulado: se imprime en consola (no se envía correo real)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Extender ALLOWED_HOSTS para desarrollo
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
