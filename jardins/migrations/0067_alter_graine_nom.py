# Generated by Django 4.2.14 on 2024-07-31 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jardins', '0066_alter_infoplante_comestibilite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graine',
            name='nom',
            field=models.CharField(blank=True, help_text='Vous pouvez indiquer un nom particulier', max_length=120, verbose_name='Nom de la graine'),
        ),
    ]
