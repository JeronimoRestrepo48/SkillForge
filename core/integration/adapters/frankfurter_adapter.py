"""
Adapter concreto: API pública Frankfurter (https://www.frankfurter.app/).
"""
from datetime import datetime, timezone

import requests
from django.conf import settings

from core.integration.adapters.base import ExchangeRateProvider, ExchangeRateResult


class FrankfurterExchangeRateAdapter(ExchangeRateProvider):
    """Implementación del contrato usando Frankfurter (sin API key)."""

    def __init__(self, base_url: str | None = None, timeout: int = 8):
        self.base_url = (base_url or settings.FRANKFURTER_API_URL).rstrip('/')
        self.timeout = timeout

    def get_rate(self, base: str, target: str) -> ExchangeRateResult:
        base = base.upper()
        target = target.upper()
        url = f'{self.base_url}/latest'
        response = requests.get(
            url,
            params={'from': base, 'to': target},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        rates = payload.get('rates') or {}
        if target not in rates:
            raise ValueError(f'Rate {base}->{target} not available from Frankfurter')
        return {
            'base': base,
            'target': target,
            'rate': float(rates[target]),
            'provider': 'frankfurter',
            'fetched_at': datetime.now(tz=timezone.utc).isoformat(),
        }
