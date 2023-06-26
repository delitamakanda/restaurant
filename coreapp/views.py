from django.shortcuts import render
from django.http import HttpResponse
from coreapp.models import Zone, Category, User, Restaurant, Meal, Order, Deliverer, Delivery
from coreapp.serializers import ZoneSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

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

