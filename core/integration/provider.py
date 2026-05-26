"""
Servicio a proveer: payload JSON público para consumo por equipos aliados.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone

from catalog.models import Curso, Categoria, EstadoCurso
from transactions.models import Orden, EstadoOrden

User = get_user_model()


def build_public_integration_payload() -> dict:
    """Información agregada del ecosistema SkillForge (sin datos personales)."""
    return {
        'team': 'SkillForge',
        'service': 'skillforge-marketplace',
        'version': '2.0.0',
        'architecture': 'hybrid-monolith-microservices',
        'timestamp': timezone.now().isoformat(),
        'stats': {
            'published_courses': Curso.objects.filter(estado=EstadoCurso.PUBLICADO).count(),
            'categories': Categoria.objects.count(),
            'registered_users': User.objects.count(),
            'confirmed_orders': Orden.objects.filter(estado=EstadoOrden.CONFIRMADA).count(),
        },
        'capabilities': [
            'jwt-api',
            'catalog',
            'checkout-strangler-flask',
            'microservices-gateway',
            'async-notifications-celery',
        ],
        'public_endpoint': '/api/integration/skillforge/public/',
    }
