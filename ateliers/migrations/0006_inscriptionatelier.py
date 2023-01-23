# Generated by Django 2.2.8 on 2019-12-09 14:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ateliers', '0005_auto_20191205_0043'),
    ]

    operations = [
        migrations.CreateModel(
            name='InscriptionAtelier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_inscription', models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscritpion")),
                ('atelier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ateliers.Atelier')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
