# -*- coding: utf-8 -*-
from .models import (Adresse, Produit, Panier, MessageAdmin, Item, Adhesion_asso, Adhesion_permacat,
                     Asso, MessageGeneral, Conversation, InscriptionNewsletter, InscriptionNewsletterAsso,
                     InvitationDansSalon, InscritSalon, Monnaie, Lien_AssoSalon)
from blog.models import (Article, Projet, FicheProjet, Commentaire, Discussion, CommentaireProjet, Evenement,
                         EvenementAcceuil, AdresseArticle
                         )
#from jardinpartage.models import Article as Art_jardin, Commentaire as Comm_jardin
from fiches.models import Fiche, Atelier as atelier_fiche, CommentaireFiche
from ateliers.models import Atelier, CommentaireAtelier, InscriptionAtelier
from agoratransition.models import InscriptionExposant, Proposition, Message_agora
from django.contrib.admin.models import LogEntry
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ProfilCreationForm, ProducteurChangeForm_admin, SalonForm
from .models import Profil, Salon
from django.utils.translation import gettext_lazy as _


@admin.register(Profil)
class CustomUserAdmin(UserAdmin):
    add_form = ProfilCreationForm
    form = ProducteurChangeForm_admin
    model = Profil
    list_display = ['id','username',  'last_login', 'email', 'date_notifications']

    readonly_fields = ('date_registration','last_login','adresse')

    fieldsets = (
        (None, {'fields': ('username','description','competences','pseudo_june', 'adherent_pc', 'adherent_rtg','adherent_fer', 'adherent_scic', 'adherent_ssa', 'adherent_citealt','adherent_viure','adherent_jp', 'adherent_conf66', 'adherent_bzz2022','adresse', 'inscrit_newsletter', 'date_notifications','accepter_annuaire', )}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', "password", )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'asso', 'categorie', 'estArchive', 'get_partagesAssotxt' )
    search_fields = ('titre', )

@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'estArchive', 'ficheprojet')
    search_fields = ('titre', )

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom_produit', 'categorie', 'estUneOffre', 'asso')
    search_fields = ('nom_produit', )

@admin.register(Adhesion_permacat)
class Adhesion_permacatAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_cotisation', 'montant')
    search_fields = ('user', )

@admin.register(Adhesion_asso)
class Adhesion_assoAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_cotisation', 'montant')
    search_fields = ('user', )

@admin.register(Asso)
class AssoAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

@admin.register(InscritSalon)
class InscritSalonAdmin(admin.ModelAdmin):
    list_display = ('salon', 'profil', 'date_creation')
    search_fields = ('salon__titre', 'profil__username', )


@admin.register(AdresseArticle)
class AdresseArticle_Admin(admin.ModelAdmin):
    list_display  = ('id', 'titre', 'adresse', 'article')
    search_fields = ('titre', )


@admin.register(Adresse)
class Adresse_Admin(admin.ModelAdmin):
    list_display  = ('id', 'rue', 'code_postal', 'commune', 'estLieAUnObjet')
    search_fields = ('rue', 'code_postal', 'commune')


@admin.register(Salon)
class Salon_Admin(admin.ModelAdmin):
    list_display  = ('titre', 'date_creation')
    search_fields = ('titre', 'description')
    #form = SalonForm


@admin.register(Lien_AssoSalon)
class LiensSalon_Admin(admin.ModelAdmin):
    list_display  = ('asso', 'salon', 'slug_type')
    search_fields = ('salon',)
    #form = SalonForm

#admin.site.register(Art_jardin, Article_jardinAdmin)
admin.site.register(MessageAdmin)
admin.site.register(Evenement)
admin.site.register(EvenementAcceuil)
admin.site.register(FicheProjet)
admin.site.register(Panier)
admin.site.register(Item)
admin.site.register(Monnaie)
admin.site.register(MessageGeneral)
admin.site.register(InscriptionNewsletter)

@admin.register(InscriptionNewsletterAsso)
class InscriptionNewsletterAsso_Admin(admin.ModelAdmin):
    list_display  = ('asso', 'nom_newsletter','email',  'profil')
    search_fields = ('email', 'nom_newsletter', 'profil__username')
    #form = SalonForm

@admin.register(Discussion)
class Discussion_Admin(admin.ModelAdmin):
    list_display  = ('article', 'titre', 'slug')
    search_fields = ('titre','article__titre')
    #form = SalonForm

admin.site.register(Conversation)
admin.site.register(Commentaire)
#admin.site.register(Comm_jardin)
admin.site.register(CommentaireProjet)

admin.site.register(Fiche)
admin.site.register(CommentaireFiche)
admin.site.register(atelier_fiche)

admin.site.register(LogEntry)

admin.site.register(Atelier)
admin.site.register(CommentaireAtelier)
admin.site.register(InscriptionAtelier)

admin.site.register(InscriptionExposant)
admin.site.register(Proposition)
admin.site.register(Message_agora)

admin.site.register(InvitationDansSalon)
