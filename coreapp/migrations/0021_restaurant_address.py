# Generated by Django 4.2.7 on 2024-05-19 18:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0020_alter_product_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='address',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='restaurants_address', to='coreapp.address'),
            preserve_default=False,
        ),
    ]