# Generated by Django 2.2.27 on 2022-04-12 07:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agoratransition', '0006_auto_20220326_1944'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='inscriptionexposant',
            unique_together={('nom', 'email')},
        ),
        migrations.AlterUniqueTogether(
            name='proposition',
            unique_together={('nom', 'email')},
        ),
    ]
