# Generated by Django 2.2.28 on 2022-08-15 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permagora', '0017_auto_20220809_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propositioncharte',
            name='existant',
            field=models.TextField(blank=True, null=True, verbose_name='Existant (ce qui se fait déjà sur le territoire : association, projet, ...)'),
        ),
    ]
