# Generated by Django 2.2.28 on 2023-01-25 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jardins', '0004_plante_lb_auteur'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plante',
            name='RANG',
            field=models.CharField(max_length=4),
        ),
    ]
