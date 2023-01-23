# Generated by Django 2.2.20 on 2021-05-26 17:46

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0019_auto_20210526_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='Liste de mots-clés séparés par une virgule', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Mots clés'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='Liste de mots-clés séparés par une virgule', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Mots clés'),
        ),
    ]
