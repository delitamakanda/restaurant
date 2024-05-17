# Generated by Django 4.2.7 on 2024-05-17 21:33

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0009_menu_remove_delivery_deliverer_remove_delivery_order_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('day', models.CharField(choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')], default='MON', max_length=3)),
                ('is_enabled', models.BooleanField(default=True)),
                ('begin_hour', models.TimeField()),
                ('end_hour', models.TimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Supplement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'verbose_name': 'Supplement',
                'verbose_name_plural': 'Supplements',
                'ordering': ['name'],
            },
        ),
        migrations.RenameField(
            model_name='address',
            old_name='user',
            new_name='customer',
        ),
        migrations.AddField(
            model_name='restaurant',
            name='menus',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='restaurants_menus', to='coreapp.menu'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image_url', models.ImageField(default='products/default.png', upload_to='products/%Y/%m/%d')),
                ('description', models.TextField()),
                ('supplements', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_supply', to='coreapp.supplement')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('order', models.PositiveIntegerField(default=1)),
                ('products', models.ManyToManyField(related_name='meals_products', to='coreapp.product')),
            ],
            options={
                'verbose_name': 'Meal',
                'verbose_name_plural': 'Meals',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='restaurant',
            name='schedule',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='restaurants_schedule', to='coreapp.schedule'),
            preserve_default=False,
        ),
    ]
