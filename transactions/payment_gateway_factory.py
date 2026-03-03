"""
Patrón Factory para la pasarela de pago.
Gestiona la dependencia externa o variante: pasarela simulada vs pasarela real (futura).
Permite cambiar el proveedor de pago sin modificar el flujo de checkout.
"""
from urllib.parse import quote
from django.urls import reverse

from transactions.models import Orden


class BasePaymentGateway:
    """Interfaz base para una pasarela de pago."""

    def get_redirect_url(self, orden: Orden, return_url: str, token: str, request=None) -> str:
        """
        Retorna la URL a la que se debe redirigir al usuario para completar el pago.
        """
        raise NotImplementedError


class SimulatedPaymentGateway(BasePaymentGateway):
    """
    Pasarela de pago simulada: redirige a la página interna de SkillForge
    donde el usuario puede elegir Pagar / Fallar / Cancelar.
    """

    def get_redirect_url(self, orden: Orden, return_url: str, token: str, request=None) -> str:
        gateway_path = reverse('transactions:checkout_gateway')
        params = (
            f'?numero_orden={quote(orden.numero_orden)}'
            f'&return_url={quote(return_url, safe="")}'
            f'&total={orden.total}'
            f'&token={quote(token, safe="")}'
        )
        path = gateway_path + params
        if request:
            return request.build_absolute_uri(path)
        return path


class PaymentGatewayFactory:
    """
    Factory que devuelve la implementación de pasarela de pago configurada.
    Por configuración (o entorno) se puede elegir simulada, Stripe, PayU, etc.
    """

    _gateway = None

    @classmethod
    def get_gateway(cls) -> BasePaymentGateway:
        """
        Retorna la instancia de pasarela de pago a usar.
        Por defecto usa la pasarela simulada; en el futuro puede leerse
        de settings (ej. PAYMENT_GATEWAY='stripe') para devolver otra implementación.
        """
        if cls._gateway is None:
            from django.conf import settings
            backend = getattr(settings, 'PAYMENT_GATEWAY_BACKEND', 'simulated')
            if backend == 'simulated':
                cls._gateway = SimulatedPaymentGateway()
            # Futuro: elif backend == 'stripe': cls._gateway = StripePaymentGateway()
            else:
                cls._gateway = SimulatedPaymentGateway()
        return cls._gateway

    @classmethod
    def reset(cls):
        """Para tests: restablece la gateway a None."""
        cls._gateway = None
