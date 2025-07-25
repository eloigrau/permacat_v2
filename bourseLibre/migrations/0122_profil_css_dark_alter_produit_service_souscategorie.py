# Generated by Django 4.2.14 on 2025-05-23 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0121_remove_profil_newsletter_envoyee_profil_adherent_ssa'),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='css_dark',
            field=models.BooleanField(default=False, verbose_name='Thème Sombre'),
        ),
        migrations.AlterField(
            model_name='produit_service',
            name='souscategorie',
            field=models.CharField(choices=[('entraide', 'entraide'), ('jardinage', 'jardinage'), ('éducation', 'éducation'), ('santé', 'santé'), ('bricolage', 'bricolage'), ('informatique', 'informatique'), ('hebergement', 'hebergement'), ('cuisine', 'cuisine'), ('batiment', 'batiment'), ('mécanique', 'mécanique'), ('autre', 'autre')], default='e', max_length=20),
        ),
    ]
