# Generated by Django 2.2.27 on 2022-04-07 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0070_auto_20220226_2208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adresse',
            name='telephone',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
