"""Health and readiness endpoints for orchestration."""
import json

from django.test import TestCase
from django.urls import reverse


class HealthEndpointsTest(TestCase):
    def test_health_liveness_returns_ok(self):
        r = self.client.get(reverse('core:health'))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertEqual(data.get('status'), 'ok')

    def test_health_ready_returns_200_when_db_and_cache_ok(self):
        r = self.client.get(reverse('core:health_ready'))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertEqual(data.get('status'), 'ready')
        self.assertEqual(data.get('checks', {}).get('database'), 'ok')
        self.assertEqual(data.get('checks', {}).get('cache'), 'ok')
