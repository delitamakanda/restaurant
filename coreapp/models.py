import uuid
from django.db import models
from django.db.models import Manager, QuerySet, Q
from django.contrib.auth.models import AbstractUser
# from django.utils import timezone
# from multiselectfield import MultiSelectField


class AppQuerySet(QuerySet):
    def delete(self):
        self.update(is_deleted=True)


class AppManager(Manager):
    def get_queryset(self):
        return AppQuerySet(self.model, using=self._db).exclude(is_deleted=True)


class TimeBasedStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    contact_number = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['username']

    def __str__(self):
        return self.username


class Tags(TimeBasedStampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='restaurant_tags')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['-name']

    def __str__(self):
        return f'{self.name} - ({self.restaurant})'


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=1)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Address(TimeBasedStampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    additional_info = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_addresses')
    digicode = models.CharField(max_length=255, blank=True, null=True)
    google_place_id = models.CharField(max_length=255, blank=True, null=True)
    icon_id = models.CharField(max_length=255, blank=True, null=True)
    lat = models.CharField(max_length=100, default=0.0)
    lng = models.CharField(max_length=100, default=0.0)
    locality = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    timezone = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.street_address}, {self.locality}, {self.postal_code}'


ALLOWED_DAYS = (
    ('MON', 'Monday'),
    ('TUE', 'Tuesday'),
    ('WED', 'Wednesday'),
    ('THU', 'Thursday'),
    ('FRI', 'Friday'),
    ('SAT', 'Saturday'),
    ('SUN', 'Sunday'),
)


class Schedule(TimeBasedStampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    day = models.CharField(max_length=3, choices=ALLOWED_DAYS, default='MON')
    is_enabled = models.BooleanField(default=True)
    begin_hour = models.TimeField()
    end_hour = models.TimeField()

    class Meta:
        ordering = ['id']
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'

    def __str__(self):
        return f'{self.day} {self.begin_hour} - {self.end_hour}'


class Restaurant(TimeBasedStampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)
    schedule = models.ManyToManyField(Schedule, related_name='restaurants_schedule')
    category = models.ManyToManyField(Category, related_name='categories')
    menus = models.ManyToManyField('Menu', related_name='restaurants_menus')
    is_deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants_user')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='restaurants_address')

    def __str__(self):
        return self.name

    class Meta:
        abstract = False
        ordering = ['name']
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'

    objects = AppManager()


class Meal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=1)
    products = models.ManyToManyField('Product', related_name='meals_products')

    class Meta:
        ordering = ['name']
        verbose_name = 'Meal'
        verbose_name_plural = 'Meals'

    def __str__(self):
        return self.name


class Supplement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Supplement'
        verbose_name_plural = 'Supplements'


class Product(TimeBasedStampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    supplements = models.ForeignKey('Supplement', on_delete=models.CASCADE, related_name='products_supply', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class Menu(TimeBasedStampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    meals = models.ManyToManyField('Meal', related_name='menus_meals')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'


class Order(models.Model):
    ORDER_STATUS = (
        (1, 'Canceled'),
        (2, 'Waiting for payment'),
        (3, 'In progress'),
        (4, 'Delivery in progress'),
        (5, 'Delivered'),
        (6, 'Waiting for consumer'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='restaurant')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=ORDER_STATUS, max_length=1, default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    canceled_at = models.DateTimeField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_by')
    is_paid = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.id

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ('name',)


class WebhookMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    received_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(default=None, blank=True, null=True)

    class Meta:
        ordering = ['-received_at']
        indexes = [models.Index(fields=['received_at'])]
