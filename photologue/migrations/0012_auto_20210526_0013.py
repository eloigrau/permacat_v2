# Generated by Django 2.2.20 on 2021-05-25 22:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0048_profil_adherent_gt'),
        ('photologue', '0011_auto_20190223_2138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='is_public',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='is_public',
        ),
        migrations.AddField(
            model_name='gallery',
            name='asso',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bourseLibre.Asso'),
        ),
        migrations.AddField(
            model_name='photo',
            name='asso',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bourseLibre.Asso'),
        ),
    ]
