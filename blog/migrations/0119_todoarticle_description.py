# Generated by Django 2.2.28 on 2024-04-16 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0118_todoarticle'),
    ]

    operations = [
        migrations.AddField(
            model_name='todoarticle',
            name='description',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
