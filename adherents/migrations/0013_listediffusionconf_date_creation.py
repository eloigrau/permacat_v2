# Generated by Django 4.2.14 on 2024-11-03 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adherents', '0012_auto_20240415_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='listediffusionconf',
            name='date_creation',
            field=models.DateTimeField(auto_now=True, verbose_name='Date de création'),
        ),
    ]
