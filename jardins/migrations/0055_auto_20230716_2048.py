# Generated by Django 2.2.28 on 2023-07-16 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jardins', '0054_auto_20230716_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grainotheque',
            name='categorie',
            field=models.CharField(choices=[('0', 'Grainothèque Collective - association'), ('2', 'Grainothèque Collective - médiathèque, école, ...'), ('3', 'Grainothèque Privée')], default='0', max_length=3, verbose_name='Type de grainotheque*'),
        ),
        migrations.AlterField(
            model_name='grainotheque',
            name='visibilite_adresse',
            field=models.CharField(choices=[('0', 'Adresse visible sans inscription'), ('1', 'Adresse visible seulement par les inscrits'), ('2', 'Adresse invisible (carte)')], default='0', max_length=30, verbose_name="Visibilité de l'adresse de la grainothèque (sur la carte)*"),
        ),
        migrations.AlterField(
            model_name='grainotheque',
            name='visibilite_annuaire',
            field=models.CharField(choices=[('0', "Public (visible dans l'annuaire sans inscription)"), ('1', 'Inscrits (visible dans seulement par les inscrits au site)'), ('2', "Invisible dans l'annuaire")], default='0', max_length=30, verbose_name="Visibilité de la grainothèque sur l'annuaire*"),
        ),
        migrations.AlterField(
            model_name='jardin',
            name='categorie',
            field=models.CharField(choices=[('0', 'Jardin Collectif - associatif'), ('1', 'Jardin Collectif - municipal'), ('2', 'Jardin Collectif - Privé'), ('3', 'Jardin Individuel - Privé'), ('', 'Jardin Professionnel (maraichage, arboriculture, etc. à usage pro)')], default='0', max_length=3, verbose_name='Type de jardin*'),
        ),
        migrations.AlterField(
            model_name='jardin',
            name='permapotes_id',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Identifiants sur permapotes.com'),
        ),
        migrations.AlterField(
            model_name='jardin',
            name='visibilite_adresse',
            field=models.CharField(choices=[('0', 'Adresse visible sans inscription'), ('1', 'Adresse visible seulement par les inscrits'), ('2', 'Adresse invisible (carte)')], default='0', max_length=30, verbose_name="Visibilité de l'adresse du jardin (sur la carte)*"),
        ),
        migrations.AlterField(
            model_name='jardin',
            name='visibilite_annuaire',
            field=models.CharField(choices=[('0', "Public (visible dans l'annuaire sans inscription)"), ('1', 'Inscrits (visible dans seulement par les inscrits au site)'), ('2', "Invisible dans l'annuaire")], default='0', max_length=3, verbose_name="Visibilité du jardin sur l'annuaire*"),
        ),
    ]
