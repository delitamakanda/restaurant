import csv
import json
import datetime
from secrets import compare_digest
from django.conf import settings
from django.db.transaction import atomic, non_atomic_requests
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from coreapp.models import Zone, Category, User, Restaurant, Meal, Order, Deliverer, Delivery, WebhookMessage
from coreapp.serializers import ZoneSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken


@csrf_exempt
@require_POST
def webhook(request):
    given_token = request.headers.get('Webhook-Token', '')
    if not compare_digest(given_token, settings.WEBHOOK_TOKEN):
        return HttpResponseForbidden(
            'Invalid webhook token',
            content_type='text/plain'
        )
    WebhookMessage.objects.filter(
        received_at__lte=timezone.now() - datetime.timedelta(days=7)
    ).delete()
    payload = json.loads(request.body.decode('utf-8'))
    WebhookMessage.objects.create(
        payload=payload,
        received_at=timezone.now()
    )
    process_webhook_payload(payload)
    return HttpResponse("Message received", content_type="text/plain")

@atomic
def process_webhook_payload(payload):
    # todo: implement business logic here
    pass


def restaurants_csv(request):
    restaurants = Restaurant.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="restaurants.csv"'
    writer = csv.writer(response)
    writer.writerow(['id', 'name', 'address', 'phone', 'email', 'zone', 'category'])
    for restaurant in restaurants:
        writer.writerow([
            restaurant.id,
            restaurant.name,
            restaurant.address,
            restaurant.phone,
            restaurant.email,
            restaurant.zone.name,
            restaurant.category.name
        ])
    return response

def hello_world_view(request):
    return HttpResponse(f'Hello world')

class ZoneListView(ModelViewSet):
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        return Zone.objects.all()

    def perform_create(self, serializer):
        serializer.save()

class APILogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if self.request.data.get('all'):
            token: OutstandingToken
            for token in OutstandingToken.objects.filter(user=request.user):
                _, _ = BlacklistedToken.objects.get_or_create(token=token)
            return Response({"status": "OK, goodbye, all refresh tokens blacklisted"})
        refresh_token = self.request.data.get('refresh_token')
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        return Response({"status": 204})

