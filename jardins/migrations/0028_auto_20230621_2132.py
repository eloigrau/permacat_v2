# Generated by Django 2.2.28 on 2023-06-21 19:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jardins', '0027_auto_20230621_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscriptionjardin',
            name='jardin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jardin_suivi', to='jardins.Jardin'),
        ),
    ]
