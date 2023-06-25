import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from multiselectfield import MultiSelectField

class User(AbstractUser):
    is_restaurant = models.BooleanField(default=False)
    is_deliverer = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=True)


class Zone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Restaurant(models.Model):
    WEEK_DAYS = (
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='restaurants/%Y/%m/%d', default='restaurants/default.png')
    opening_days = MultiSelectField(choices=WEEK_DAYS, max_length=2)
    opening_hours = models.DateTimeField(blank=True, null=True)
    closing_hours = models.DateTimeField(blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories')
    zone = models.ManyToManyField(Zone, related_name='restaurants')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'

class Meal(models.Model):
    OPTIONS_MEAL = (
        ('HA', 'Halal'),
        ('CA', 'Casher'),
        ('VE', 'Vegetarian'),
        ('VA', 'Vegan'),
    )
    CATEGORY_MEAL = (
        ('EN', 'Entrees'),
        ('ME', 'Meals'),
        ('AC', 'Accompaniements'),
        ('TO', 'Toppings'),
        ('FO', 'Formula'),
        ('DE', 'Desserts'),
        ('DR', 'Drinks'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='meals/%Y/%m/%d', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='meals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    options = MultiSelectField(choices=OPTIONS_MEAL, max_length=2)
    category = models.CharField(max_length=2, choices=CATEGORY_MEAL, default='ME')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Meal'
        verbose_name_plural = 'Meals'

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
    meals = models.ManyToManyField(Meal, related_name='meals')
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

class Deliverer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user', blank=True, null=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    zone = models.ManyToManyField(Zone, related_name='deliverer')

    class Meta:
        ordering = ['name']
        verbose_name = 'Deliverer'
        verbose_name_plural = 'Deliverers'
    
    def __str__(self):
        return self.name

class Delivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order')
    deliverer = models.ForeignKey(Deliverer, on_delete=models.CASCADE, related_name='deliverer')
    delivered_at = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.id

    class Meta:
        ordering = ['-delivered_at']
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'

