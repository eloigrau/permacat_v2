# Generated by Django 2.2.28 on 2023-01-25 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jardins', '0006_auto_20230125_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plante',
            name='CD_TAXSUP',
            field=models.CharField(max_length=5),
        ),
    ]