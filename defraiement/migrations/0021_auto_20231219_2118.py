# Generated by Django 2.2.28 on 2023-12-19 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defraiement', '0020_distance_participantreunion_type_trajet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distance_participantreunion',
            name='distance',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Distance calculée'),
        ),
    ]
