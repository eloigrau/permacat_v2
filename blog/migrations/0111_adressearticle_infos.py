# Generated by Django 2.2.28 on 2024-01-25 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0110_auto_20231025_1054'),
    ]

    operations = [
        migrations.AddField(
            model_name='adressearticle',
            name='infos',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Infos complémentaires'),
        ),
    ]
