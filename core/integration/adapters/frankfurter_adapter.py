"""
Adapter concreto: API pública Frankfurter v2 (https://frankfurter.dev/).
"""
from datetime import datetime, timezone

import requests
from django.conf import settings

from core.integration.adapters.base import ExchangeRateProvider, ExchangeRateResult


class FrankfurterExchangeRateAdapter(ExchangeRateProvider):
    """Implementación del contrato usando Frankfurter v2 (sin API key)."""

    def __init__(self, base_url: str | None = None, timeout: int = 8):
        self.base_url = (base_url or settings.FRANKFURTER_API_URL).rstrip('/')
        self.timeout = timeout

    def get_rate(self, base: str, target: str) -> ExchangeRateResult:
        base = base.upper()
        target = target.upper()
        url = f'{self.base_url}/v2/rate/{base}/{target}'
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        rate = payload.get('rate')
        if rate is None:
            raise ValueError(f'Rate {base}->{target} not available from Frankfurter')
        return {
            'base': payload.get('base', base),
            'target': payload.get('quote', target),
            'rate': float(rate),
            'provider': 'frankfurter',
            'fetched_at': datetime.now(tz=timezone.utc).isoformat(),
        }
