# Generated by Django 2.2.24 on 2021-09-07 14:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0070_evenement_auteur'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evenement',
            name='auteur',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
