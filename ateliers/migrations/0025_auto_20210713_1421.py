# Generated by Django 2.2.24 on 2021-07-13 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ateliers', '0024_auto_20210706_2220'),
    ]

    operations = [
        migrations.RenameField(
            model_name='atelier',
            old_name='date_atelier',
            new_name='start_time',
        ),
    ]
