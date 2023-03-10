# Generated by Django 2.2.27 on 2022-02-26 20:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0068_auto_20220224_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='Produit_offresEtDemandes',
            fields=[
                ('produit_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bourseLibre.Produit')),
                ('couleur', models.CharField(choices=[('#f2c7f1', '#f2c7f1')], default='#f2c7f1', max_length=20)),
                ('souscategorie', models.CharField(choices=[('Liste', 'Liste')], default='L', max_length=20)),
                ('type_prix', models.CharField(choices=[('kg', 'kg'), ('100g', '100g'), ('10g', '10g'), ('g', 'g'), ('un', 'unité'), ('li', 'litre')], default='kg', max_length=20, verbose_name='par')),
            ],
            bases=('bourseLibre.produit',),
        ),
        migrations.DeleteModel(
            name='Produit_listeOffresEtDemandes',
        ),
    ]
