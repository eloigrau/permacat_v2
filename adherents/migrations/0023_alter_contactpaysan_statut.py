# Generated by Django 4.2.14 on 2024-11-17 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adherents', '0022_alter_paysan_adherent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactpaysan',
            name='statut',
            field=models.CharField(choices=[('0', 'Réponse_OK'), ('1', 'Pas de réponse'), ('2', 'A répondu mais à rappeler'), ('3', 'A répondu mais HOSTILE'), ('4', 'Mauvais numéroe')], default='0', max_length=2, verbose_name='Statut'),
        ),
    ]
