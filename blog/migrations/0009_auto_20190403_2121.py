# Generated by Django 2.1.7 on 2019-04-03 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20190403_1950'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commentaire',
            name='titre',
        ),
        migrations.RemoveField(
            model_name='commentaireprojet',
            name='titre',
        ),
        migrations.AddField(
            model_name='projet',
            name='coresponsable',
            field=models.CharField(blank=True, default='', max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='projet',
            name='date_modification',
            field=models.DateTimeField(auto_now=True, verbose_name='Date de dernière modification'),
        ),
        migrations.AddField(
            model_name='projet',
            name='lien_document',
            field=models.URLField(blank=True, default='', null=True, verbose_name='Lien vers un document explicatif (en ligne)'),
        ),
        migrations.AddField(
            model_name='projet',
            name='lien_vote',
            field=models.URLField(blank=True, null=True, verbose_name='Lien vers le vote (balotilo.org)'),
        ),
        migrations.AddField(
            model_name='projet',
            name='fichier',
            field=models.FileField(blank=True, default=None, null=True, upload_to='projets/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='projet',
            name='date_fichier',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='projet',
            name='statut',
            field=models.CharField(choices=[('prop', 'Proposition'), ('AGO', "Soumis à l'AGO"), ('vote', 'Soumis au vote'), ('accep', 'Accepté'), ('refus', 'Refusé')], default='prop', max_length=5, verbose_name='statut'),
        ),
        migrations.AlterField(
            model_name='projet',
            name='categorie',
            field=models.CharField(choices=[('Part', 'Participation à un évènement'), ('AGO', "Organisation d'une AGO"), ('Projlong', 'Projet a long terme'), ('Projcourt', 'Projet a court terme')], default='Part', max_length=10, verbose_name='categorie'),
        ),

    ]
