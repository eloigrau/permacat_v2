# Generated by Django 2.2.24 on 2022-02-09 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defraiement', '0005_auto_20220206_2341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reunion',
            name='categorie',
            field=models.CharField(choices=[('0', 'Rencontre'), ('1', 'Troc de Graine'), ('2', 'Atelier'), ('3', 'Réunion'), ('4', 'Autre')], default='0', max_length=30, verbose_name='categorie'),
        ),
    ]
