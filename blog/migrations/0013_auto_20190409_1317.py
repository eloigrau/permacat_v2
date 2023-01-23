# Generated by Django 2.1.3 on 2019-04-09 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_auto_20190408_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='estArchive',
            field=models.BooleanField(default=False, verbose_name="Archiver l'artcle (il n'apparaitra plus)"),
        ),
        migrations.AlterField(
            model_name='projet',
            name='estArchive',
            field=models.BooleanField(default=False, verbose_name="Archiver le projet (il n'apparaitra plus)"),
        ),
        migrations.AlterField(
            model_name='projet',
            name='statut',
            field=models.CharField(choices=[('prop', 'Proposition de projet'), ('AGO', "Soumis à l'AGO"), ('vote', 'Soumis au vote'), ('accep', "Accepté par l'association"), ('refus', "Refusé par l'association")], default='prop', max_length=5, verbose_name='statut'),
        ),
    ]
