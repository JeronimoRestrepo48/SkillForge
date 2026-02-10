"""
Configuración base de Django para SkillForge.
Común a todos los entornos (desarrollo, producción).
"""
import environ
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

# Cargar .env si existe
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))

SECRET_KEY = env('SECRET_KEY', default='dev-key-change-in-production')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'rest_framework_simplejwt',
    # Local apps
    'core',
    'users',
    'catalog',
    'transactions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.carrito_cantidad',
            ],
        },
    },
]

# Database - override in development.py or production.py
_default_db = f'sqlite:///{BASE_DIR}/db.sqlite3'
DATABASES = {
    'default': env.db('DATABASE_URL', default=_default_db)
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / 'locale']

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email (simulado en desarrollo; override en producción)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@skillforge.local')

# Auth
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# REST Framework y JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
