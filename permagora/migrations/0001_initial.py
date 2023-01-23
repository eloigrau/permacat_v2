# Generated by Django 2.2.4 on 2019-08-17 21:57

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('description', models.TextField(blank=True, null=True)),
                ('date_registration', models.DateTimeField(editable=False, verbose_name='Date de création')),
                ('inscrit_newsletter', models.BooleanField(default=False, verbose_name="J'accepte de recevoir des emails")),
                ('accepter_conditions', models.BooleanField(default=False, verbose_name="J'ai lu et j'accepte les conditions d'utilisation du site")),
                ('accepter_annuaire', models.BooleanField(default=True, verbose_name="J'accepte d'apparaitre dans l'annuaire du site et la carte et rend mon profil visible par tous")),
                ('a_signe', models.BooleanField(default=False, verbose_name="J'ai signé la charte")),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Adresse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_postal', models.CharField(blank=True, default='66000', max_length=5, null=True)),
                ('commune', models.CharField(blank=True, default='Perpignan', max_length=50, null=True)),
                ('latitude', models.FloatField(blank=True, default='42.6976', null=True)),
                ('longitude', models.FloatField(blank=True, default='2.8954', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('type_message', models.CharField(choices=[('0', 'commentaire'), ('1', 'coquille'), ('2', 'Reflexion')], default='0', max_length=10, verbose_name='type de message')),
                ('type_article', models.CharField(choices=[('0', 'intro'), ('1', 'constat'), ('2', 'preconisations'), ('3', 'charte'), ('4', 'liens'), ('5', 'accueil')], default='0', max_length=10, verbose_name='reaction à')),
                ('valide', models.BooleanField(default=False, verbose_name='validé')),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='profil',
            name='adresse',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='permagora.Adresse'),
        ),
        migrations.AddField(
            model_name='profil',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='profil',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
