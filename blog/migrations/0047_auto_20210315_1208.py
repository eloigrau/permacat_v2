# Generated by Django 2.2.13 on 2021-03-15 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0046_auto_20210315_1156'),
    ]

    operations = [
        migrations.RenameField(
            model_name='evenement',
            old_name='titre',
            new_name='titre_even',
        ),
        migrations.RenameField(
            model_name='evenementacceuil',
            old_name='titre',
            new_name='titre_even',
        ),
    ]
