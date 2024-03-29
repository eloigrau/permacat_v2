# Generated by Django 2.2.28 on 2023-10-26 17:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0107_salon_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListeDiffusion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='InscriptionListeDiffusion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('date_inscription', models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")),
                ('commentaire', models.CharField(blank=True, max_length=50)),
                ('asso', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bourseLibre.Asso')),
                ('liste_diffusion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='liste_diffusion', to='bourseLibre.ListeDiffusion', verbose_name='Liste de diffusion')),
                ('profil', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profil_listediff', to=settings.AUTH_USER_MODEL, verbose_name='Profil du membre (si inscrit)')),
            ],
        ),
    ]
