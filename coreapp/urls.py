from .views import hello_world_view, ZoneListView, APILogoutView
from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r'api/v1/zones-lists', ZoneListView, basename='zones-lists')

urlpatterns = [
    path('hello', hello_world_view, name='hello'),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/logout/', APILogoutView.as_view(), name='logout_view'),
]

urlpatterns += router.urls