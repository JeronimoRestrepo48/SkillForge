"""
Servicio a consumir: cliente HTTP del endpoint público del equipo aliado.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger('django.request')


def fetch_ally_public_data() -> dict:
    """
    Consume el JSON del equipo aliado. Si no hay URL configurada, devuelve
    un mock documentado para desarrollo local y sustentación.
    """
    url = (settings.ALLY_SERVICE_URL or '').strip()
    if not url:
        return _mock_ally_payload()

    endpoint = settings.ALLY_SERVICE_PUBLIC_PATH
    full_url = f'{url.rstrip("/")}/{endpoint.lstrip("/")}'
    try:
        response = requests.get(full_url, timeout=settings.ALLY_SERVICE_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        data['meta'] = {'source': 'ally-live', 'url': full_url}
        return data
    except requests.RequestException as exc:
        logger.warning('Ally service unavailable: %s', exc)
        fallback = _mock_ally_payload()
        fallback['meta'] = {
            'source': 'ally-fallback',
            'error': str(exc),
            'attempted_url': full_url,
        }
        return fallback


def _mock_ally_payload() -> dict:
    """Contrato de ejemplo cuando el aliado aún no expone su IP (desarrollo)."""
    return {
        'team': 'Ally Team (mock)',
        'service': 'ally-learning-hub',
        'version': '1.0.0',
        'architecture': 'monolith',
        'timestamp': None,
        'stats': {
            'published_courses': 8,
            'categories': 4,
            'registered_users': 42,
            'confirmed_orders': 15,
        },
        'capabilities': ['catalog-api', 'enrollments'],
        'public_endpoint': '/api/integration/ally/public/',
        'meta': {
            'source': 'mock',
            'hint': 'Set ALLY_SERVICE_URL to the ally EC2 base URL (e.g. http://3.x.x.x)',
        },
    }
