# Generated by Django 2.2.28 on 2024-04-16 13:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0117_auto_20240408_1638'),
    ]

    operations = [
        migrations.CreateModel(
            name='TodoArticle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=150)),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('date_modification', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
                ('estFait', models.BooleanField(default=False)),
                ('article', models.ForeignKey(help_text='Article lié', on_delete=django.db.models.deletion.CASCADE, to='blog.Article')),
                ('slug', models.SlugField( max_length=100),),
            ],
        ),
    ]
