# Generated by Django 2.2.28 on 2023-01-25 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jardins', '0014_auto_20230126_0023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dbhabitat_inpn',
            name='LB_HABITAT',
            field=models.TextField(null=True),
        ),
    ]
