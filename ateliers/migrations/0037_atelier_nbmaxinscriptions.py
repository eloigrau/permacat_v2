# Generated by Django 2.2.28 on 2024-04-03 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ateliers', '0036_auto_20230920_1402'),
    ]

    operations = [
        migrations.AddField(
            model_name='atelier',
            name='nbMaxInscriptions',
            field=models.IntegerField(blank=True, null=True, verbose_name="Nombre maximum d'inscriptions"),
        ),
    ]
