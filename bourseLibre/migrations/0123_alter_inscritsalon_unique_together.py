# Generated by Django 4.2.14 on 2025-06-19 12:37

from django.db import migrations


def supprimer_doublons(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    inscriptions = apps.get_model('bourseLibre', 'InscritSalon')
    for insc in inscriptions.objects.all():
        double = inscriptions.objects.filter(salon=insc.salon, profil=insc.profil)
        if len(double) > 1:
            for d in double[1:]:
                d.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0122_profil_css_dark_alter_produit_service_souscategorie'),
    ]

    operations = [

        migrations.RunPython(supprimer_doublons, ),
        migrations.AlterUniqueTogether(
            name='inscritsalon',
            unique_together={('salon', 'profil')},
        ),
    ]
