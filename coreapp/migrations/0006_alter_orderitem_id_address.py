# Generated by Django 4.2 on 2023-06-26 19:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0005_orderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('zip_code', models.CharField(max_length=10)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
                'ordering': ('title',),
            },
        ),
    ]
