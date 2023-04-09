from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, Group
from coreapp.models import (
    User,
    Zone,
    Category,
    Restaurant,
    Meal,
    Order,
    Deliverer,
    Delivery,
)

admin.site.register(User)
admin.site.unregister(Group)
admin.site.register(Zone)
admin.site.register(Category)
admin.site.register(Restaurant)
admin.site.register(Meal)
admin.site.register(Order)
admin.site.register(Deliverer)
admin.site.register(Delivery)
