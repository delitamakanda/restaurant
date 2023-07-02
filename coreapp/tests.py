import datetime
from http import HTTPStatus
from django.test import TestCase, override_settings, Client
from django.utils import timezone

from .models import WebhookMessage

@override_settings(WEBHOOK_TOKEN='1234567890')
class WebhookTestCase(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_bad_method(self):
        response = self.client.get('/api/webhook/')
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_missing_token(self):
        response = self.client.post('/api/webhook/')
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.content.decode('utf-8') == 'Invalid webhook token'
    
    def test_bad_token(self):
        response = self.client.post('/api/webhook/', HTTP_WEBHOOK_TOKEN='badtoken')
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.content.decode('utf-8') == 'Invalid webhook token'

    def test_success(self):
        start = timezone.now()
        old_message = WebhookMessage.objects.create(
            received_at=start - datetime.timedelta(days=100),
        )
        response = self.client.post('/api/webhook/', HTTP_WEBHOOK_TOKEN='1234567890', content_type="application/json", data={ "foo": "bar" })
        assert response.status_code == HTTPStatus.OK
        assert response.content.decode('utf-8') == 'Message received'
        assert WebhookMessage.objects.filter(id=old_message.id).exists()
        wm = WebhookMessage.objects.filter(id=old_message.id).first()
        assert wm.received_at >= start
        assert wm.payload == None
