# Generated by Django 2.2.28 on 2022-12-11 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defraiement', '0015_auto_20221113_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reunion',
            name='categorie',
            field=models.CharField(choices=[('0', 'Réunion équipe'), ('1', 'Troc de Graine'), ('2', 'Atelier'), ('3', 'Rencontre'), ('4', 'Réunion FestiGraines'), ('5', 'Autre'), ('6', 'Cercle Ancrage'), ('7', 'Cercle thématique'), ('8', 'Cercle Education'), ('9', 'Cercle Jardins'), ('10', 'Evenement'), ('11', 'Divers')], default='0', max_length=30, verbose_name='categorie'),
        ),
    ]
