# Generated by Django 4.2 on 2023-04-09 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliverer',
            name='zone',
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='zone',
        ),
        migrations.AddField(
            model_name='deliverer',
            name='zone',
            field=models.ManyToManyField(related_name='deliverer', to='coreapp.zone'),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='zone',
            field=models.ManyToManyField(related_name='restaurants', to='coreapp.zone'),
        ),
    ]
