# Generated by Django 2.1.3 on 2019-04-16 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0015_auto_20190410_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='estModifiable',
            field=models.BooleanField(default=False, verbose_name="Modifiable par n'importe qui"),
        ),
    ]
