# Generated by Django 2.2.28 on 2024-03-27 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0115_auto_20240219_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adressearticle',
            name='infos',
            field=models.TextField(blank=True, null=True, verbose_name='Infos complémentaires'),
        ),
    ]
