# Generated by Django 4.2.14 on 2025-04-10 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0126_alter_article_categorie'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleLiens',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('type_lien', models.CharField(choices=[('0', 'sous-article'), ('1', 'article connexe'), ('2', 'Autre')], default='0', max_length=2)),
                ('article', models.ForeignKey(help_text='Article de base', on_delete=django.db.models.deletion.CASCADE, to='blog.article')),
                ('article_lie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='article_lie', to='blog.article')),
            ],
        ),
        migrations.CreateModel(
            name='ArticleLienProjet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('type_lien', models.CharField(choices=[('0', 'info projet'), ('1', 'info connexe'), ('3', 'Autre')], default='0', max_length=2)),
                ('article', models.ForeignKey(help_text='Article de base', on_delete=django.db.models.deletion.CASCADE, to='blog.article')),
                ('projet_lie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projet_lie', to='blog.projet')),
            ],
        ),
        # migrations.CreateModel(
        #     name='Article_recherche',
        #     fields=[
        #         ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.article')),
        #     ],
        # ),
    ]
