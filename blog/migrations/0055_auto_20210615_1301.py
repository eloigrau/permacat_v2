# Generated by Django 2.2.24 on 2021-06-15 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0054_merge_20210526_2244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='titre',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='projet',
            name='titre',
            field=models.CharField(max_length=250),
        ),
    ]
