# Generated by Django 2.2.20 on 2021-05-27 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0022_album_estmodifiable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(upload_to='photologue', verbose_name='image'),
        ),
    ]
