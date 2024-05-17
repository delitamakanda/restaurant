# Generated by Django 4.2.7 on 2024-05-17 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0015_alter_product_image_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='menus',
        ),
        migrations.AddField(
            model_name='restaurant',
            name='menus',
            field=models.ManyToManyField(related_name='restaurants_menus', to='coreapp.menu'),
        ),
    ]