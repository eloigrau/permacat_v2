# Generated by Django 4.2.14 on 2025-07-09 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0134_alter_salon_type_salon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produit',
            name='estPublique',
        ),
        migrations.AlterField(
            model_name='produit',
            name='date_debut',
            field=models.DateField(blank=True, null=True, verbose_name='Débute le '),
        ),
        migrations.AlterField(
            model_name='produit',
            name='date_expiration',
            field=models.DateField(blank=True, null=True, verbose_name='Expire le '),
        ),
        migrations.AlterField(
            model_name='produit',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name="Description de l'annonce"),
        ),
        migrations.AlterField(
            model_name='produit',
            name='prix',
            field=models.CharField(blank=True, max_length=150, verbose_name='Tarif (si besoin)'),
        ),
    ]
