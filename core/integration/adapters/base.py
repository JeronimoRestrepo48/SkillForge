"""
Patrón Adapter (inversión de dependencias): contrato para proveedores de tipo de cambio.
La aplicación depende de esta abstracción, no de la API HTTP concreta.
"""
from abc import ABC, abstractmethod
from typing import TypedDict


class ExchangeRateResult(TypedDict):
    base: str
    target: str
    rate: float
    provider: str
    fetched_at: str


class ExchangeRateProvider(ABC):
    @abstractmethod
    def get_rate(self, base: str, target: str) -> ExchangeRateResult:
        """Obtiene el tipo de cambio base -> target."""
