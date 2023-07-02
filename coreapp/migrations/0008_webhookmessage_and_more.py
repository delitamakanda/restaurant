# Generated by Django 4.2 on 2023-07-02 18:06

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0007_restaurant_address_restaurant_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebhookMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                ('payload', models.JSONField(blank=True, default=None, null=True)),
            ],
            options={
                'ordering': ['-received_at'],
            },
        ),
        migrations.AddIndex(
            model_name='webhookmessage',
            index=models.Index(fields=['received_at'], name='coreapp_web_receive_35ee73_idx'),
        ),
    ]