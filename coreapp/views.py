import csv
import json
import datetime
from secrets import compare_digest
from django.conf import settings
from django.db.transaction import atomic
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from coreapp.models import (
    Category,
    User,
    Restaurant,
    Menu,
    WebhookMessage,
    Meal,
    Product,
    Tags,
)
from coreapp.response import response_handler
from coreapp.pagination import handle_pagination


@csrf_exempt
def list_users(request):
    if request.method == "GET":
        """
        List all users.

        Args:
            request (HttpRequest): Request object.

        Returns:
            HttpResponse: API response.
        """
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 10)
        search = request.GET.get("search", "")

        users = User.objects.filter(
            username__icontains=search,
        ).order_by("id")

        paginator = handle_pagination(page, per_page, users)
        return JsonResponse(
            response_handler(
                data={
                    "users": [
                        {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "contact_number": user.contact_number,
                            "contact_email": user.contact_email,
                            "date_joined": user.date_joined.isoformat(),
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "is_active": user.is_active,
                            "is_staff": user.is_staff,
                        }
                        for user in paginator.object_list
                    ],
                    "search": search,
                }
            )
        )
    else:
        return JsonResponse(
            response_handler({}, status_code=405, message="Method not allowed")
        )


@csrf_exempt
def list_restaurants(request):
    if request.method == "GET":
        """
        List all restaurants.

        Args:
            request (HttpRequest): Request object.

        Returns:
            HttpResponse: API response.
        """
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 20)
        search = request.GET.get("search", "")
        categories = request.GET.getlist("categories", [])

        restaurants = Restaurant.objects.filter(
            is_deleted=False,
            name__icontains=search,
        ).prefetch_related("menus", "menus__meals__products")

        if categories:
            restaurants = restaurants.filter(category__id__in=categories)

        paginator = handle_pagination(page, per_page, restaurants)

        return JsonResponse(
            response_handler(
                data={
                    "restaurants": [
                        restaurant.serialize() for restaurant in paginator.object_list
                    ],
                    "total_pages": paginator.paginator.num_pages,
                    "current_page": paginator.number,
                    "per_page": paginator.paginator.per_page,
                }
            ),
            status=200,
        )
    return JsonResponse(
        response_handler({}, status_code=405, message="Method not allowed")
    )


@csrf_exempt
def list_categories(request):
    if request.method == "GET":
        """
        List all categories.

        Args:
            request (HttpRequest): Request object.

        Returns:
            HttpResponse: API response.
        """
        categories = Category.objects.order_by("position").values(
            "id", "name", "position", "image_url"
        )
        return JsonResponse(
            response_handler(
                data={
                    "categories": list(categories),
                }
            ),
            status=200,
        )
    return JsonResponse(
        response_handler({}, status_code=405, message="Method not allowed")
    )


@csrf_exempt
def list_products(request):
    if request.method == "GET":
        """
        List all products.

        Args:
            request (HttpRequest): Request object.

        Returns:
            HttpResponse: API response.
        """
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 99)
        search = request.GET.get("search", "")

        products = Product.objects.filter(
            name__icontains=search,
            description__icontains=search,
        ).prefetch_related("supplements")

        paginator = handle_pagination(page, per_page, products)

        return JsonResponse(
            response_handler(
                data={
                    "products": [
                        product.serialize() for product in paginator.object_list
                    ],
                    "total_pages": paginator.paginator.num_pages,
                    "current_page": paginator.number,
                    "per_page": paginator.paginator.per_page,
                    "search": search,
                },
            )
        )
    return JsonResponse(
        response_handler({}, status_code=405, message="Method not allowed")
    )


@csrf_exempt
def list_meals(request):
    if request.method == "GET":
        """
        List all meals.

        Args:
            request (HttpRequest): Request object.

        Returns:
            HttpResponse: API response.
        """
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 99)
        search = request.GET.get("search", "")

        meals = Meal.objects.filter(
            name__icontains=search,
        ).prefetch_related("products")

        paginator = handle_pagination(page, per_page, meals)
        return JsonResponse(
            response_handler(
                data={
                    "meals": [meal.serialize() for meal in paginator.object_list],
                    "total_pages": paginator.paginator.num_pages,
                    "current_page": paginator.number,
                    "per_page": paginator.paginator.per_page,
                    "search": search,
                }
            )
        )
    return JsonResponse(
        response_handler({}, status_code=405, message="Method not allowed")
    )


@csrf_exempt
def list_menus(request):
    if request.method == "GET":
        """
        List all menus.

        Args:
            request (HttpRequest): Request object.

        Returns:
            HttpResponse: API response.
        """
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 99)
        search = request.GET.get("search", "")

        menus = Menu.objects.filter(
            name__icontains=search,
        ).prefetch_related("meals")

        paginator = handle_pagination(page, per_page, menus)

        return JsonResponse(
            response_handler(
                data={
                    "menus": [menu.serialize() for menu in paginator.object_list],
                    "total_pages": paginator.paginator.num_pages,
                    "current_page": paginator.number,
                    "per_page": paginator.paginator.per_page,
                    "search": search,
                }
            )
        )
    return JsonResponse(
        response_handler({}, status_code=405, message="Method not allowed")
    )


# class TemplateViewSet(ModelViewSet):
#     permission_classes = [
#         AllowAny,
#     ]
#     lookup_field = "id"
#     lookup_url_kwarg = "id"
#     http_method_names = [
#         "get",
#     ]
#
#
# class MenuViewSet(TemplateViewSet):
#     queryset = Menu.objects.all()
#     serializer_class = MenuSerializer
#
#
# class UserViewSet(TemplateViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#
# class MealViewSet(TemplateViewSet):
#     queryset = Meal.objects.all()
#     serializer_class = MealSerializer
#
#
# class ProductViewSet(TemplateViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#
# class CategoryViewSet(TemplateViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#
#
# class RestaurantViewSet(TemplateViewSet):
#     queryset = Restaurant.objects.all()
#     serializer_class = RestaurantSerializer


@csrf_exempt
@require_POST
def webhook(request):
    given_token = request.headers.get("Webhook-Token", "")
    if not compare_digest(given_token, settings.WEBHOOK_TOKEN):
        return HttpResponseForbidden("Invalid webhook token", content_type="text/plain")
    WebhookMessage.objects.filter(
        received_at__lte=timezone.now() - datetime.timedelta(days=7)
    ).delete()
    payload = json.loads(request.body.decode("utf-8"))
    WebhookMessage.objects.create(payload=payload, received_at=timezone.now())
    process_webhook_payload(payload)
    return HttpResponse("Message received", content_type="text/plain")


@atomic
def process_webhook_payload(payload):
    # todo: implement business logic here
    pass


def restaurants_csv(request):
    restaurants = Restaurant.objects.all()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="restaurants.csv"'
    writer = csv.writer(response)
    writer.writerow(["id", "name", "address", "phone", "email", "category"])
    for restaurant in restaurants:
        writer.writerow(
            [
                restaurant.id,
                restaurant.name,
                restaurant.address,
                restaurant.phone,
                restaurant.email,
                restaurant.category.name,
            ]
        )
    return response


def hello_world_view(request):
    return HttpResponse("Hello world")


@csrf_exempt
def list_tags(request):
    if request.method == "GET":
        """
        List all tags.

        Args:
            request (HttpRequest): Request object.

        Returns:
            HttpResponse: API response.
        """
        tags = Tags.objects.all().values(
            "id",
            "name",
        )
        print(tags)

        return JsonResponse(
            response_handler(data=[tag.serialize() for tag in tags], status_code=200)
        )
    return JsonResponse(
        response_handler({}, status_code=405, message="Method not allowed")
    )


@csrf_exempt
def api_root(request):
    return JsonResponse(
        response_handler(
            data={
                "products": "/api/products/",
                "meals": "/api/meals/",
                "menus": "/api/menus/",
                "tags": "/api/tags/",
                "restaurants": "/api/restaurants/",
                "users": "/api/users/",
                "categories": "/api/categories/",
                "webhook": "/api/webhook/",
            },
            status_code=200,
        )
    )


@csrf_exempt
def handler_404(request, exception):
    return redirect(reverse("api_root"))
