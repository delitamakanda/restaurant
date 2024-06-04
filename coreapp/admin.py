from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, Group

from coreapp.models import (
    User,
    Category,
    Restaurant,
    Menu,
    Order,
    OrderItem,
    WebhookMessage,
    Meal,
    Supplement,
    Product,
    Address,
    Schedule,
    Tags,
)


class CustomUserAdmin(UserAdmin):
    list_display: tuple[str, str, str] = (
        "id",
        "username",
        "email",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "email",
                    "password",
                    "contact_number",
                    "first_name",
                    "last_name",
                    "contact_email",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "contact_number",
                    "first_name",
                    "last_name",
                    "contact_email",
                ),
            },
        ),
    )


class SupplementInline(admin.StackedInline):
    model = Supplement


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "price",
        "supplements",
    )


class RestaurantAdmin(admin.ModelAdmin):
    inlines = []


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(Category)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Meal)
admin.site.register(Product, ProductAdmin)
admin.site.register(Address)
admin.site.register(Schedule)
admin.site.register(Menu)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(WebhookMessage)
admin.site.register(Tags)
