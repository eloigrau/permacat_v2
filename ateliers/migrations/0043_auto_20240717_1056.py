# Generated by Django 2.2.28 on 2024-07-17 08:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ateliers', '0042_auto_20240717_1010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commentaireatelier_new',
            name='atelier',
        ),
        migrations.RemoveField(
            model_name='commentaireatelier_new',
            name='auteur_comm',
        ),
        migrations.RemoveField(
            model_name='inscriptionatelier_new',
            name='atelier',
        ),
        migrations.RemoveField(
            model_name='inscriptionatelier_new',
            name='user',
        ),
        migrations.DeleteModel(
            name='Atelier_new',
        ),
        migrations.DeleteModel(
            name='CommentaireAtelier_new',
        ),
        migrations.DeleteModel(
            name='InscriptionAtelier_new',
        ),
    ]
