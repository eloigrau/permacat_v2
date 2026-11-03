from django.db import migrations, models

def make_all_documents_public(apps, schema_editor):
    # Récupère le modèle de manière sécurisée sans l'importer directement en haut du fichier
    Document = apps.get_model('photologue', 'Document')

    # Met à jour tous les documents existants
    Document.objects.all().update(visibility='membre')

def reverse_make_public(apps, schema_editor):
    # Optionnel : ce qui se passe si on fait un rollback (retour en arrière)
    # Par exemple, on remet tout le monde à 'authenticated'
    Document = apps.get_model('photologue', 'Document')
    Document.objects.all().update(visibility='public')

class Migration(migrations.Migration):
    dependencies = [
        ('photologue', '0039_alter_document_visibility'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='visibility',
            field=models.CharField(choices=[('public', 'Public (Accessible à tous)'), ('authenticated', 'Connectés (Tous les inscrits)'), ('membre', 'Membre du Groupe'), ('restricted', 'Restreint (Groupes spécifiques)')], default='membre', help_text='Restriction ou pas pour le téléchargement du fichier', max_length=20, verbose_name='Visibilité'),
        ),
        migrations.RunPython(make_all_documents_public, reverse_make_public),
    ]