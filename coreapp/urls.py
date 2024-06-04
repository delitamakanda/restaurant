from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    hello_world_view,
    RestaurantViewSet,
    CategoryViewSet,
    ProductViewSet,
    MealViewSet,
    APILogoutView,
    restaurants_csv,
    UserViewSet,
    MenuViewSet,
    webhook,
)

router = routers.DefaultRouter()
router.register(r"api/restaurants-list", RestaurantViewSet, basename="restaurants-list")
router.register(r"api/categories-list", CategoryViewSet, basename="categories-list")
router.register(r"api/products-list", ProductViewSet, basename="products-list")
router.register(r"api/meals-list", MealViewSet, basename="meals-list")
router.register(r"api/users-list", UserViewSet, basename="users-list")
router.register(r"api/menus-list", MenuViewSet, basename="menus-list")

urlpatterns = [
    path("hello", hello_world_view, name="hello"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/logout/", APILogoutView.as_view(), name="logout_view"),
    # webhook
    path("api/webhook/", webhook, name="webhook"),
    # CSV
    path("api/restaurants/csv/", restaurants_csv, name="restaurants_csv"),
]

urlpatterns += router.urls
