# Generated by Django 2.2.28 on 2022-08-20 13:12

from django.db import migrations
from django.utils.timezone import now

def combine_names(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    profilModel = apps.get_model('bourseLibre', 'Profil')
    addresseModel = apps.get_model('bourseLibre', 'Adresse')
    add = addresseModel.objects.create()
    add.save()
    bot, created = profilModel.objects.get_or_create(username='bot_permacat',
                                                email="eloi.grau@gmail.com",
                                                accepter_annuaire=False,
                                                date_registration=now(),
                                                 adresse=add,
                                                )


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0079_salon_article'),
    ]

    operations = [
        migrations.RunPython(combine_names, ),

    ]
