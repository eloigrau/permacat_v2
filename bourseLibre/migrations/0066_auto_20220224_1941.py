# Generated by Django 2.2.27 on 2022-02-24 18:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0065_adhesion_permacat_moyen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adhesion_permacat',
            name='montant',
            field=models.CharField(max_length=50, verbose_name="Montant de l'adhesion"),
        ),
        migrations.AlterField(
            model_name='adhesion_permacat',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur Permacat'),
        ),
    ]
