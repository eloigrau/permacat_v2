# Generated by Django 2.2.28 on 2023-01-25 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jardins', '0016_auto_20230126_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plante',
            name='infos_supp',
            field=models.TextField(null=True),
        ),
    ]