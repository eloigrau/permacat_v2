# Generated by Django 4.2.14 on 2025-05-15 20:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0119_alter_favoris_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='asso',
            old_name='abreviation',
            new_name='slug',
        ),
    ]
