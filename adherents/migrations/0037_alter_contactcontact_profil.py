# Generated by Django 4.2.14 on 2025-01-19 21:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('adherents', '0036_alter_contactcontact_statut'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactcontact',
            name='profil',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Auteur'),
        ),
    ]
