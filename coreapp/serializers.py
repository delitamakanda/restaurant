from django.db import IntegrityError
from rest_framework import serializers

from coreapp.models import (Category, User, Restaurant, Meal, Order, OrderItem, Menu,
                            Product, Supplement, Address, Schedule, Tags)


class TemplateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        try:
            return self.Meta.model.objects.create(**validated_data)
        except IntegrityError as e:
            raise serializers.ValidationError(str(e))


class TagsSerializer(TemplateSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = Menu
        fields = '__all__'


class SupplementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplement
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    supplements = SupplementSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id',)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    restaurant = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'contact_email',
                  'contact_number', 'first_name', 'last_name', 'is_active', 'is_staff',
                  'restaurant',)

    @staticmethod
    def get_restaurant(obj):
        restaurant = Restaurant.objects.filter(user=obj)
        return [restaurant.id for restaurant in restaurant.all()]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'position', 'image_url',)


class RestaurantSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    address = AddressSerializer(many=False, read_only=True)
    schedule = ScheduleSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'image_url', 'category', 'address', 'tags',
                  'schedule', 'menus', 'is_deleted', 'user')
        read_only_fields = ('id',)

    @staticmethod
    def get_tags(obj):
        tags = Tags.objects.filter(restaurant=obj)
        return [tag.name for tag in tags.all()]


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
