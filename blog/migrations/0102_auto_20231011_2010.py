# Generated by Django 2.2.28 on 2023-10-11 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0101_auto_20230920_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='categorie',
            field=models.CharField(choices=[('Annonce', 'Annonce'), ('Administratif', 'Organisation'), ('Agenda', 'Agenda'), ('Chantier', 'Atelier/Chantier participatif'), ('Documentation', 'Documentation'), ('covoit', 'Covoiturage'), ('Point', 'Idée / Point de vue'), ('Recette', 'Recette'), ('BonPlan', 'Bon Plan / achat groupé'), ('Divers', 'Divers'), ('Altermarché', 'Altermarché'), ('Ecovillage', 'Ecovillage'), ('Jardin', 'Jardins partagés'), ('ChantPossible', 'Ecolieu Chant des possibles'), ('BD_Fred', 'Les BD de Frédéric'), ('bzzz', 'Projet Bzzzz'), ('professionel', 'Activité Pro'), ('sante', 'Santé et Bien-être'), ('orga1', 'Cercle Organisation'), ('orga2', 'Cercle Informatique'), ('orga3', 'Cercle Communication'), ('orga4', 'Cercle Animation'), ('orga5', 'Cercle Médiation'), ('theme1', 'Cercle Education'), ('theme2', 'Cercle Ecolieux'), ('theme3', 'Cercle Santé'), ('theme4', 'Cercle Echanges'), ('theme5', 'Cercle Agriculture'), ('theme6', 'Cercle Célébration'), ('groupe1', 'Groupe de Perpignan'), ('groupe2', 'Groupe des Albères'), ('groupe3', 'Groupe des Aspres'), ('groupe4', 'Groupe du Vallespir'), ('groupe5', 'Groupe du Ribéral'), ('groupe7', 'Groupe du Conflent'), ('groupe6', 'Groupe de la côte'), ('Info', 'Annonce / Information'), ('Agenda', 'Agenda'), ('coordination', 'Coordination'), ('reunion', 'Réunions'), ('manifestations', 'Manifestations'), ('projets', 'Projets écocides'), ('AgendaBzz', 'AgendaBzz'), ('Documentation', 'Documentation'), ('rendez-vous', 'Rendez-vous'), ('Discu', 'Information'), ('Organisation', 'Organisation'), ('Potager', 'Au potager'), ('Documentation', 'Documentation'), ('Autre', 'Autre'), ('jardin_0', 'Jardin_0'), ('jardin_1', 'Jardin_1'), ('jardin_2', 'Jardin_2'), ('jardin_3', 'Jardin_3'), ('jardin_4', 'Jardin_4'), ('jardin_5', 'Jardin_5'), ('jardin_6', 'Jardin_6'), ('jardin_7', 'Jardin_7'), ('jardin_8', 'Jardin_8'), ('jardin_9', 'Jardin_9'), ('jardin_10', 'Jardin_10'), ('jardin_11', 'Jardin_11'), ('jardin_12', 'Jardin_12'), ('jardin_13', 'Jardin_13'), ('jardin_14', 'Jardin_14'), ('jardin_15', 'Jardin_15'), ('jardin_16', 'Jardin_16'), ('jardin_17', 'Jardin_17'), ('jardin_18', 'Jardin_18'), ('jardin_19', 'Jardin_19'), ('jardin_20', 'Jardin_20'), ('jardin_21', 'Jardin_21'), ('jardin_22', 'Jardin_22'), ('jardin_23', 'Jardin_23'), ('jardin_24', 'Jardin_24'), ('jardin_25', 'Jardin_25'), ('jardin_26', 'Jardin_26'), ('jardin_27', 'Jardin_27'), ('jardin_28', 'Jardin_28'), ('jardin_29', 'Jardin_29'), ('jardin_30', 'Jardin_30'), ('jardin_31', 'Jardin_31'), ('jardin_32', 'Jardin_32'), ('jardin_33', 'Jardin_33'), ('jardin_34', 'Jardin_34'), ('jardin_35', 'Jardin_35'), ('jardin_36', 'Jardin_36'), ('jardin_37', 'Jardin_37'), ('jardin_38', 'Jardin_38'), ('jardin_39', 'Jardin_39'), ('jardin_40', 'Jardin_40'), ('jardin_41', 'Jardin_41'), ('jardin_42', 'Jardin_42'), ('jardin_43', 'Jardin_43'), ('jardin_44', 'Jardin_44'), ('jardin_45', 'Jardin_45'), ('jardin_46', 'Jardin_46'), ('jardin_47', 'Jardin_47'), ('jardin_48', 'Jardin_48'), ('jardin_49', 'Jardin_49'), ('jardin_50', 'Jardin_50'), ('jardin_51', 'Jardin_51'), ('jardin_52', 'Jardin_52'), ('jardin_53', 'Jardin_53'), ('jardin_54', 'Jardin_54'), ('jardin_55', 'Jardin_55'), ('jardin_56', 'Jardin_56'), ('jardin_57', 'Jardin_57'), ('jardin_58', 'Jardin_58'), ('jardin_59', 'Jardin_59'), ('jardin_60', 'Jardin_60'), ('jardin_61', 'Jardin_61'), ('jardin_62', 'Jardin_62'), ('jardin_63', 'Jardin_63'), ('jardin_64', 'Jardin_64'), ('jardin_65', 'Jardin_65'), ('jardin_66', 'Jardin_66'), ('jardin_67', 'Jardin_67'), ('jardin_68', 'Jardin_68'), ('jardin_69', 'Jardin_69'), ('jardin_70', 'Jardin_70'), ('jardin_71', 'Jardin_71'), ('jardin_72', 'Jardin_72'), ('jardin_73', 'Jardin_73'), ('jardin_74', 'Jardin_74'), ('jardin_75', 'Jardin_75'), ('jardin_76', 'Jardin_76'), ('jardin_77', 'Jardin_77'), ('jardin_78', 'Jardin_78'), ('jardin_79', 'Jardin_79'), ('jardin_80', 'Jardin_80'), ('jardin_81', 'Jardin_81'), ('jardin_82', 'Jardin_82'), ('jardin_83', 'Jardin_83'), ('jardin_84', 'Jardin_84'), ('jardin_85', 'Jardin_85'), ('jardin_86', 'Jardin_86'), ('jardin_87', 'Jardin_87'), ('jardin_88', 'Jardin_88'), ('jardin_89', 'Jardin_89'), ('jardin_90', 'Jardin_90'), ('jardin_91', 'Jardin_91'), ('jardin_92', 'Jardin_92'), ('jardin_93', 'Jardin_93'), ('jardin_94', 'Jardin_94'), ('jardin_95', 'Jardin_95'), ('jardin_96', 'Jardin_96'), ('jardin_97', 'Jardin_97'), ('jardin_98', 'Jardin_98'), ('jardin_99', 'Jardin_99'), ('Annonce', 'Annonce'), ('Administratif', 'Organisation'), ('Agenda', 'Agenda'), ('Cercle0', "Cercle d'Ancrage"), ('Cercle1', 'Cercle Education'), ('Cercle2', 'Cercle Jardins'), ('Cercle3', 'Cercle Thématique'), ('Cercle4', 'Cercle Communication'), ('Cercle5', 'Cercle Partenariat'), ('Cercle6', 'Cercle Evenementiel'), ('Annonce', 'Annonce'), ('administratif', 'Administratif'), ('elevage', 'Elevage'), ('apiculture', 'Apiculture'), ('maraichage', 'Maraichage'), ('arboriculture', 'Arboriculture'), ('arboriculture', 'Arboriculture'), ('Commission', 'Commission'), ('Infos', 'Infos diverses')], default='', max_length=30, verbose_name='Dossier'),
        ),
    ]
