# Generated by Django 2.2.28 on 2023-06-21 12:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bourseLibre', '0098_auto_20230225_0207'),
        ('jardins', '0024_auto_20230127_2259'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Jardin',
            new_name='Plante_recherche',
        ),
        migrations.CreateModel(
            name='Jardins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categorie', models.CharField(choices=[('0', 'Collectif'), ('1', 'Privé'), ('2', 'Associatif'), ('3', 'Familial'), ('4', 'Ouvrier')], default='', max_length=30, verbose_name='Type de jardin')),
                ('visibilite', models.CharField(choices=[('0', 'Public'), ('1', 'Adhérents_site'), ('2', 'Invisible')], default='', max_length=30, verbose_name='Visibilité du jardin sur le site')),
                ('titre', models.CharField(max_length=250)),
                ('slug', models.SlugField(max_length=100)),
                ('description', models.TextField(null=True)),
                ('parcellesIndividuelles', models.BooleanField(default=False, verbose_name='Parcelles Individuelles')),
                ('parcellesCollectives', models.BooleanField(default=False, verbose_name='Parcelles Collectives')),
                ('email_contact', models.EmailField(max_length=254)),
                ('telephone', models.CharField(blank=True, max_length=15, verbose_name='Numéroe de telephone de contact')),
                ('adresse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bourseLibre.Adresse')),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auteur_jardin', to=settings.AUTH_USER_MODEL)),
                ('referent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referent_jardin', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Grainotheque',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visibilite', models.CharField(choices=[('0', 'Public'), ('1', 'Adhérents_site'), ('2', 'Invisible')], default='', max_length=30, verbose_name='Visibilité de la grainotheque sur le site')),
                ('titre', models.CharField(max_length=250)),
                ('slug', models.SlugField(max_length=100)),
                ('liste_plantes', models.TextField(null=True)),
                ('adresse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bourseLibre.Adresse')),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auteur_grainotheque', to=settings.AUTH_USER_MODEL)),
                ('jardin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jardins.Jardins')),
                ('referent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referent_grainotheque', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
