from .views import hello_world_view
from django.urls import path

urlpatterns = [
    path('hello', hello_world_view, name='hello')
]