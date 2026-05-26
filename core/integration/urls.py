from django.urls import path

from core.integration.views import ExchangeRateAPIView, SkillForgePublicIntegrationAPIView

app_name = 'integration'

urlpatterns = [
    path(
        'skillforge/public/',
        SkillForgePublicIntegrationAPIView.as_view(),
        name='skillforge_public',
    ),
    path('exchange-rate/', ExchangeRateAPIView.as_view(), name='exchange_rate'),
]
