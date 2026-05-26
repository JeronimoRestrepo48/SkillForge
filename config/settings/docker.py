"""
Configuración para despliegue en Docker / AWS (HTTP detrás de Nginx).
"""
from .base import *  # noqa: F401, F403

DEBUG = env.bool('DEBUG', default=False)

# Servir CSS/JS/imágenes con collectstatic (DEBUG=False en Docker)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    *[
        m
        for m in MIDDLEWARE
        if m
        not in (
            'django.middleware.security.SecurityMiddleware',
            'whitenoise.middleware.WhiteNoiseMiddleware',
        )
    ],
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Respeta ALLOWED_HOSTS del .env (no sobrescribir como en development.py)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'nginx'])

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
