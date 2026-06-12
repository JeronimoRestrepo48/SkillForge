from celery import Celery
from app.config import settings

# Inicializamos una aplicación Celery apuntando al broker de Redis del ecosistema.
# Esto nos permite usar celery_app.send_task('task_name', args=[...]) para interactuar con
# los workers Celery (como el de Django) sin importar todo el framework Django.
celery_app = Celery(
    "skillforge",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configuramos serialización simple JSON para compatibilidad
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC"
)
