# Generated by Django 2.2.28 on 2023-01-25 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jardins', '0005_auto_20230125_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plante',
            name='CD_REF',
            field=models.CharField(max_length=5),
        ),
        migrations.AlterField(
            model_name='plante',
            name='CD_SUP',
            field=models.CharField(max_length=5),
        ),
    ]
