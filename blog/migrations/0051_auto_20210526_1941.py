# Generated by Django 2.2.20 on 2021-05-26 17:41

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0050_auto_20210526_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Mots clés'),
        ),
        migrations.AlterField(
            model_name='projet',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Mots clés'),
        ),
    ]
