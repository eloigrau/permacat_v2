# Generated by Django 2.2.28 on 2023-11-24 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adherents', '0005_adherent_production_ape'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adherent',
            name='nom',
            field=models.CharField(max_length=120, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='adherent',
            name='prenom',
            field=models.CharField(blank=True, max_length=120, verbose_name='Prénom'),
        ),
        migrations.AlterField(
            model_name='adherent',
            name='statut',
            field=models.CharField(choices=[('0', 'Inconnu'), ('1', 'A titre principal'), ('2', 'Cotisant Solidaire'), ('3', 'CC'), ('4', 'Retraité')], default='0', max_length=5, verbose_name="Statut d'agriculteur"),
        ),
    ]
