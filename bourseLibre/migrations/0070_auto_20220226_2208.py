# Generated by Django 2.2.27 on 2022-02-26 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0069_auto_20220226_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produit_offresetdemandes',
            name='souscategorie',
            field=models.CharField(choices=[('Liste', 'Liste')], default='Liste', max_length=20),
        ),
    ]
