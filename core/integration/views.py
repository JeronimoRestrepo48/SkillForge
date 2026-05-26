from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.integration.adapters import FrankfurterExchangeRateAdapter
from core.integration.ally_consumer import fetch_ally_public_data
from core.integration.provider import build_public_integration_payload


class SkillForgePublicIntegrationAPIView(APIView):
    """
    Servicio a proveer (Entregable 2): JSON público del ecosistema SkillForge.
    GET /api/integration/skillforge/public/
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(build_public_integration_payload())


class ExchangeRateAPIView(APIView):
    """
    Consumo de API de terceros vía Adapter (Frankfurter).
    GET /api/integration/exchange-rate/?base=USD&target=COP
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        base = (request.query_params.get('base') or 'USD').upper()
        target = (request.query_params.get('target') or 'COP').upper()
        adapter = FrankfurterExchangeRateAdapter()
        try:
            data = adapter.get_rate(base, target)
            return Response(data)
        except Exception as exc:
            return Response(
                {'detail': 'Unable to fetch exchange rate.', 'error': str(exc)},
                status=503,
            )


@method_decorator(cache_page(60), name='dispatch')
class IntegrationHubView(LoginRequiredMixin, TemplateView):
    """UI: muestra datos del aliado y tipo de cambio (tercero vía Adapter)."""

    template_name = 'integration_hub.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ally_data'] = fetch_ally_public_data()
        context['our_public'] = build_public_integration_payload()
        adapter = FrankfurterExchangeRateAdapter()
        try:
            context['exchange_rate'] = adapter.get_rate('USD', 'COP')
            context['exchange_error'] = None
        except Exception as exc:
            context['exchange_rate'] = None
            context['exchange_error'] = str(exc)
        return context
