import os
from celery import Celery

_REDIS_URL = os.environ.get('CELERY_BROKER_URL', os.environ.get('REDIS_URL', 'redis://redis:6379/0'))
_DEFAULT_RESULT_BACKEND = _REDIS_URL.rsplit('/', 1)[0] + '/1' if '/' in _REDIS_URL.rsplit('//', 1)[-1] else 'redis://redis:6379/1'
_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', _DEFAULT_RESULT_BACKEND)

celery_app = Celery('skillforge', broker=_REDIS_URL, backend=_RESULT_BACKEND)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Bogota',
)
