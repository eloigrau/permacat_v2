# Generated by Django 2.2.28 on 2023-10-20 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defraiement', '0016_auto_20221211_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reunion',
            name='categorie',
            field=models.CharField(choices=[('0', 'Réunion équipe'), ('1', 'Troc de Graine'), ('2', 'Atelier'), ('3', 'Rencontre'), ('4', 'FestiGraines'), ('5', 'Visite de Jardin'), ('6', 'Autre'), ('7', 'Cercle Ancrage'), ('8', 'Cercle thématique'), ('9', 'Cercle Education'), ('10', 'Cercle Jardins'), ('11', 'Evenement'), ('12', 'Divers')], default='0', max_length=30, verbose_name='categorie'),
        ),
    ]
