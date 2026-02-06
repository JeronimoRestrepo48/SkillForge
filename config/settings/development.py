"""
Configuración específica para desarrollo.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

# Extender ALLOWED_HOSTS para desarrollo
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
