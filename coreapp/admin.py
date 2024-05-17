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
)


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'is_restaurant', 'is_guest',)
    list_filter = ('is_restaurant', 'is_guest',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_restaurant', 'is_guest')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'is_active', 'is_staff', 'is_superuser', 'is_restaurant', 'is_guest'),
        }),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(Category)
admin.site.register(Restaurant)
admin.site.register(Meal)
admin.site.register(Supplement)
admin.site.register(Product)
admin.site.register(Address)
admin.site.register(Schedule)
admin.site.register(Menu)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(WebhookMessage)
