# Generated by Django 2.2.28 on 2023-02-25 01:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0097_auto_20230225_0145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produit_aliment',
            name='couleur',
        ),
        migrations.RemoveField(
            model_name='produit_objet',
            name='couleur',
        ),
        migrations.RemoveField(
            model_name='produit_offresetdemandes',
            name='couleur',
        ),
        migrations.RemoveField(
            model_name='produit_service',
            name='couleur',
        ),
        migrations.RemoveField(
            model_name='produit_vegetal',
            name='couleur',
        ),
    ]
