# Generated by Django 2.2.28 on 2023-09-20 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0105_auto_20230824_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='adherent_conf66',
            field=models.BooleanField(default=False, verbose_name='Je suis adhérent à la confédération Paysanne 66'),
        ),
    ]
