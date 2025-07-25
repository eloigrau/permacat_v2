# Generated by Django 4.2.14 on 2024-12-04 15:06

from django.db import migrations, models



def copierListesDiffusion(apps, schema_migration):
    Assos = apps.get_model('bourseLibre', 'Asso')
    asso_conf = Assos.objects.get(slug="conf66")

    Projets = apps.get_model('adherents', 'ProjetPhoning')
    projet_conf = Projets.objects.create(titre="EP CA 2024", asso=asso_conf)

    Contacts = apps.get_model('adherents', 'Contact')

    for a in Contacts.objects.all():
        a.projet = projet_conf
        a.save(update_fields=["projet", ])

class Migration(migrations.Migration):

    dependencies = [
        ('adherents', '0030_remove_contactcontact_paysan'),
    ]

    operations = [

        migrations.RunPython(copierListesDiffusion)
    ]
