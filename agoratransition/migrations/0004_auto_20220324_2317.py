# Generated by Django 2.2.27 on 2022-03-24 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agoratransition', '0003_auto_20220324_2308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscriptionexposant',
            name='statut_exposant',
            field=models.CharField(choices=[('0', 'Inscription déposée'), ('1', 'Inscription incomplète ou en cours de validation'), ('5', 'Inscription valide mais en attente du cheque de caution'), ('2', 'Inscription validée'), ('3', 'Inscription refusée'), ('4', 'Inscription annulée')], default='0', max_length=3, verbose_name='Statut'),
        ),
        migrations.AlterField(
            model_name='inscriptionexposant',
            name='type_inscription',
            field=models.CharField(choices=[('0', 'Particulier'), ('1', 'Association'), ('2', 'Institution'), ('3', 'Entreprise'), ('4', 'autre')], default='0', max_length=3, verbose_name='Type de structure'),
        ),
    ]
