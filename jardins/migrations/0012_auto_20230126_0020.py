# Generated by Django 2.2.28 on 2023-01-25 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jardins', '0011_auto_20230125_2349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dbstatut_inpn',
            name='DESCRIPTION',
            field=models.CharField(max_length=150),
        ),
    ]