# Generated by Django 2.2.24 on 2021-07-04 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0025_auto_20210615_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='title',
            field=models.CharField(blank=True, max_length=250, verbose_name='title'),
        ),
    ]
