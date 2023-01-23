# Generated by Django 2.2.8 on 2020-01-06 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0024_auto_20200105_2246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='end_time',
            field=models.DateTimeField(blank=True, help_text='jj/mm/année', null=True, verbose_name='Date de fin'),
        ),
        migrations.AlterField(
            model_name='article',
            name='start_time',
            field=models.DateTimeField(blank=True, help_text='jj/mm/année', null=True, verbose_name='Date de début'),
        ),
        migrations.AlterField(
            model_name='projet',
            name='end_time',
            field=models.DateTimeField(blank=True, help_text='jj/mm/année', null=True, verbose_name='Date de fin'),
        ),
        migrations.AlterField(
            model_name='projet',
            name='start_time',
            field=models.DateTimeField(blank=True, help_text='jj/mm/année', null=True, verbose_name='Date de début'),
        ),
    ]
