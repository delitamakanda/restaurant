# Generated by Django 4.2.7 on 2024-05-17 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0014_remove_meal_products_remove_menu_meals_meal_products_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
