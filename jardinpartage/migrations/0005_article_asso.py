# Generated by Django 2.2.13 on 2020-08-25 20:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bourseLibre', '0033_auto_20200825_2014'),
        ('jardinpartage', '0004_participation'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='asso',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asso_article_jardin', to='bourseLibre.Asso'),
        ),
    ]
