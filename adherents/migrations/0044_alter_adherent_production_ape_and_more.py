# Generated by Django 4.2.14 on 2025-07-02 21:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adherents', '0043_inscriptionmail_email_pasadherent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adherent',
            name='production_ape',
            field=models.CharField(blank=True, max_length=120, verbose_name='Production (APE)'),
        ),
        migrations.AlterField(
            model_name='adhesion',
            name='adherent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adherents.adherent', verbose_name='Adhérent'),
        ),
    ]
