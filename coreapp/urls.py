from django.urls import path

from coreapp.views import (
    hello_world_view,
    restaurants_csv,
    webhook,
    list_products,
    list_restaurants,
    list_categories,
    list_meals,
    list_menus,
    list_users,
    list_tags,
    api_root,
    get_restaurant_by_id,
)


handler404 = "coreapp.views.handler_404"  # replace with your custom 404 view handler function name if needed


urlpatterns = [
    path("", api_root, name="api_root"),
    # hello world view
    path("hello", hello_world_view, name="hello"),
    # webhook
    path("api/webhook/", webhook, name="webhook"),
    # CSV
    path("api/restaurants/csv/", restaurants_csv, name="restaurants_csv"),
    path("api/restaurants/", list_restaurants, name="list_restaurants"),
    path("api/categories/", list_categories, name="list_categories"),
    path("api/products/", list_products, name="list_products"),
    path("api/meals/", list_meals, name="list_meals"),
    path("api/menus/", list_menus, name="list_menus"),
    path("api/users/", list_users, name="list_users"),
    path("api/tags/", list_tags, name="list_tags"),
    path(
        "api/restaurants/<int:restaurant_id>/",
        get_restaurant_by_id,
        name="get_restaurant_by_id",
    ),
]
