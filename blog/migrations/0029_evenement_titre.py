# Generated by Django 2.2.8 on 2020-02-17 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0028_evenement'),
    ]

    operations = [
        migrations.AddField(
            model_name='evenement',
            name='titre',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]
