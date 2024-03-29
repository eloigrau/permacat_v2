# Generated by Django 2.2.28 on 2023-10-16 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0104_auto_20231011_2049'),
    ]

    operations = [
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='themes',
            field=models.ManyToManyField(blank=True, related_name='themes', to='blog.Theme', verbose_name='Thèmes :'),
        ),
    ]
