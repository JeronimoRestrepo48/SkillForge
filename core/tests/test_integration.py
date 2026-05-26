from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from core.integration.adapters.frankfurter_adapter import FrankfurterExchangeRateAdapter
from core.integration.provider import build_public_integration_payload


class PublicIntegrationAPITest(TestCase):
    def test_public_provider_returns_json(self):
        client = APIClient()
        response = client.get(reverse('integration:skillforge_public'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['team'], 'SkillForge')
        self.assertIn('stats', response.json())

    def test_build_payload_has_stats(self):
        payload = build_public_integration_payload()
        self.assertIn('published_courses', payload['stats'])


class ExchangeRateAdapterTest(TestCase):
    @patch('core.integration.adapters.frankfurter_adapter.requests.get')
    def test_adapter_maps_frankfurter_response(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {'rates': {'COP': 4200.5}},
        )
        adapter = FrankfurterExchangeRateAdapter(base_url='https://api.frankfurter.app')
        result = adapter.get_rate('USD', 'COP')
        self.assertEqual(result['base'], 'USD')
        self.assertEqual(result['target'], 'COP')
        self.assertEqual(result['rate'], 4200.5)
        self.assertEqual(result['provider'], 'frankfurter')


@override_settings(ALLY_SERVICE_URL='')
class AllyConsumerMockTest(TestCase):
    def test_mock_when_no_ally_url(self):
        from core.integration.ally_consumer import fetch_ally_public_data

        data = fetch_ally_public_data()
        self.assertEqual(data['_meta']['source'], 'mock')
