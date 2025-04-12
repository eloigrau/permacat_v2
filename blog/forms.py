from django import forms
from bourseLibre.models import Salon, InscritSalon
from .models import Article, Article_recherche, Commentaire, Projet, Projet_recherche, FicheProjet, CommentaireProjet, Evenement, AdresseArticle, \
    DocumentPartage, Discussion, Choix, Theme, AssociationSalonArticle, TodoArticle, ArticleLiens, ArticleLienProjet
from django.utils.text import slugify
import itertools
from local_summernote.widgets import SummernoteWidget
from django.urls import reverse
from bourseLibre.settings import SUMMERNOTE_CONFIG as summernote_config
from bourseLibre.models import Asso, Choix as choix_globaux
from defraiement.models import Reunion
from django.templatetags.static import static
from photologue.models import Album
from django.core.exceptions import ValidationError
from django.db.models import Q
import re
from bourseLibre.utils import slugify_pcat
from dal import autocomplete
#from taggit.models import Tag

class DateInput(forms.DateInput):
    input_type = 'date'

class SummernoteWidgetWithCustomToolbar(SummernoteWidget):
    def summernote_settings(self):
        summernote_settings = summernote_config.get('summernote', {}).copy()

        lang = summernote_config['summernote'].get('lang')
        if not lang:
            lang = 'fr-FR'
        summernote_settings.update({
            'lang': lang,
            'url': {
                'language': static('summernote/lang/summernote-' + lang + '.min.js'),
                'upload_attachment': reverse('local_summernote-upload_attachment'),
            },
                # As an example, using Summernote Air-mode
                'airMode': False,
                'iFrame': False,

                # Change editor size
                'width': '100%',
                'height': '360',

                # Use proper language setting automatically (default)

            "toolbar": [
                ['emoji', ['emoji']],
                ['style', ['bold', 'italic', 'underline', 'clear', 'style', ]],
                ['fontsize', ['fontsize']],
                ['fontSizes', ['8', '9', '10', '11', '12', '14', '18', '22', '24', '36']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['link', ['link', 'picture', 'video', 'table', 'hr', ]],
                ['misc', ['undo', 'redo', 'help', 'fullscreen', 'codeview', 'readmore']],

            ],
            "popover": {
                "image": [
                    ['imagesize', ['imageSize100', 'imageSize50', 'imageSize25']],
                    ['float', ['floatLeft', 'floatRight', 'floatNone']],
                    ['remove', ['removeMedia']]
                ],
                "link": [
                    ['link', ['linkDialogShow', 'unlink']]
                ],
                "air": [
                ['emoji', ['emoji']],
                ['style', ['bold', 'italic', 'underline', 'clear', 'style', ]],
                ['fontsize', ['fontsize']],
                ['fontSizes', ['8', '9', '10', '11', '12', '14', '18', '22', '24', '36']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['link', ['link', 'picture', 'video', 'table', 'hr', ]],
                ['misc', ['undo', 'redo', 'help', 'fullscreen']],
                ]
            },
        })
        return summernote_settings

class ArticleForm(forms.ModelForm):
    asso = forms.ModelChoiceField(queryset=Asso.objects.all().order_by("id"), required=True,
                              label="Article public ou réservé aux membres du groupe :", )

    partagesAsso = forms.ModelMultipleChoiceField(label='Partager avec :', required=False, queryset=Asso.objects.order_by("id"),
                                             widget=forms.CheckboxSelectMultiple(attrs={'class': 'cbox_asso', }) )

    #themes = forms.ModelMultipleChoiceField(label='Thèmes :', required=False, queryset=Theme.objects.all(),
    #                                         widget=forms.CheckboxSelectMultiple(attrs={'class': 'cbox_asso', }) )

    class Meta:
        model = Article
        fields = ['asso', 'partagesAsso', 'categorie', 'titre', 'contenu', 'start_time', 'tags', 'zonegeo', 'estModifiable', 'estEpingle', ]
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time':  forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
              'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
           # 'tags': autocomplete.TaggitSelect2(
           #     'blog:tag_autocomplete'
            #),
        }

    def save(self, userProfile, sendMail=True, forcerCreationMails=False):
        instance = super(ArticleForm, self).save(commit=False)

        max_length = Article._meta.get_field('slug').max_length
        instance.slug = orig = slugify_pcat(instance.titre, max_length)

        for x in itertools.count(1):
            if not Article.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        if len(re.findall(r"[A-Z]", instance.titre)) > 8:
            instance.titre = instance.titre.title()

        instance.auteur = userProfile
        instance.save(sendMail=sendMail, forcerCreationMails=forcerCreationMails)
        return instance

    def __init__(self, request, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields["asso"].choices = [('', '(Choisir un groupe)'), ] + [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if request.user.estMembre_str(x.abreviation)]
        self.fields["categorie"].choices = [('', "(Choisir d'abord un groupe ci-dessus)"), ] #+ list(Choix.get_type_annonce_asso(""))

        if 'asso' in self.data:
            try:
                asso_id = int(self.data.get('asso'))
                nomAsso = Asso.objects.get(id=asso_id).abreviation
                self.fields["categorie"].choices = Choix.get_type_annonce_asso(nomAsso)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields["categorie"].choices = Choix.get_type_annonce_asso("")



class ArticleChangeForm(forms.ModelForm):
    partagesAsso = forms.ModelMultipleChoiceField(label='Partager avec :', required=False, queryset=Asso.objects.order_by("id"),
                                             widget=forms.CheckboxSelectMultiple(attrs={'class': 'cbox_asso', }) )

    themes = forms.ModelMultipleChoiceField(label='Thèmes :', required=False, queryset=Theme.objects.all(),
                                             widget=forms.CheckboxSelectMultiple(attrs={'class': 'cbox_asso', }) )
    description_modif = forms.CharField(label="Description courte de la modification de l'article", required=False, )

    class Meta:
        model = Article
        fields = ['asso', 'partagesAsso', 'categorie', 'titre', 'contenu', 'start_time', 'album', 'zonegeo', 'themes', 'tags', 'estModifiable', 'estArchive', 'estEpingle', ]
        widgets = {
            'contenu': SummernoteWidget(),
            'start_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def save(self, sendMail=True, commit=True):
        instance = super(ArticleChangeForm, self).save(commit=commit)
        #ModificationArticle.objects.create(article=instance, description=self.cleaned_data['description_modif'])

        for asso in Asso.objects.all():
            if asso in self.cleaned_data["partagesAsso"]:
                instance.partagesAsso.add(asso)
            elif instance.partagesAsso.filter(abreviation=asso.abreviation).exists():
                instance.partagesAsso.remove(asso)
        for theme in Theme.objects.all():
            if theme in self.cleaned_data["themes"]:
                instance.themes.add(theme)
            elif instance.themes.filter(nom=theme.nom).exists():
                instance.themes.remove(theme)
        return instance

#
# class ModificationArticleForm(forms.ModelForm):
#     class Meta:
#         model = ModificationArticle
#         fields = ['description',]


class AssociationSalonArticleForm(forms.ModelForm):

    class Meta:
        model = AssociationSalonArticle
        fields = ['salon',]

    def save(self, article):
        instance = super(AssociationSalonArticleForm, self).save(commit=False)
        instance.article = article
        instance.save()
        return instance

    def __init__(self, request, *args, **kwargs):
        super(AssociationSalonArticleForm, self).__init__(*args, **kwargs)
        salons_inscrit = InscritSalon.objects.filter(profil=request.user, salon__estPublic=False).order_by( "salon__titre")
        salons = [x for x in Salon.objects.filter(estPublic=True).order_by("titre")] + [s.salon for s in salons_inscrit]
        self.fields["salon"].choices = [(x.id, x.titre) for x in salons]

class ArticleAddAlbum(forms.ModelForm):
    album = forms.ModelChoiceField(queryset=Album.objects.all(), required=True,
                              label="Si l'album existe déjà sur le site, choisissez l'album photo à associer ci-dessous", )

    class Meta:
        model = Article
        fields = ['album',]


class DiscussionForm(forms.ModelForm):

    class Meta:
        model = Discussion
        exclude = ['article', 'slug']

    def valider_unique(self, article):
        cleaned_data = self.cleaned_data

        try:
            Discussion.objects.get(slug=slugify(cleaned_data['titre']), article=article)
        except Discussion.DoesNotExist:
            pass
        else:
            raise ValidationError('Il existe déjà une discussion avec ce titre pour cet article')

        # Always return cleaned_data
        return cleaned_data

class CommentaireArticleForm(forms.ModelForm):

    class Meta:
        model = Commentaire
        exclude = ['article', 'auteur_comm', 'discussion']
        #
        widgets = {
         'commentaire': SummernoteWidgetWithCustomToolbar(),
        }

    def __init__(self, request, *args, **kwargs):
        super(CommentaireArticleForm, self).__init__(request, *args, **kwargs)
        self.fields['commentaire'].strip = False

class CommentaireArticleChangeForm(forms.ModelForm):
    commentaire = forms.CharField(required=False, widget=SummernoteWidget(attrs={}))

    class Meta:
        model = Commentaire
        exclude = ['article', 'auteur_comm', 'discussion']

    #def __init__(self, request, article=None, *args, **kwargs):
    #    super(CommentaireArticleChangeForm, self).__init__(request, *args, **kwargs)
     #   self.fields['commentaire'].strip = False
        #if article:
        #    self.fields['discussion'] = forms.ModelChoiceField(queryset=Discussion.objects.filter(article=article), required=True,)


class ProjetForm(forms.ModelForm):
    asso = forms.ModelChoiceField(queryset=Asso.objects.all(), required=True,
                              label="Projet public ou réservé aux adhérents de l'asso :", )
    class Meta:
        model = Projet
        fields = ['asso', 'categorie', 'coresponsable', 'titre', 'contenu', 'statut', 'tags',  'start_time']
        widgets = {
        'contenu': SummernoteWidget(),
              'start_time':forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
              'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def __init__(self, request, *args, **kwargs):
        super(ProjetForm, self).__init__(*args, **kwargs)
        self.fields['contenu'].strip = False
        self.fields["asso"].choices = [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if request.user.estMembre_str(x.abreviation)]

    def save(self, userProfile, sendMail=True):
        instance = super(ProjetForm, self).save(commit=False)

        max_length = Projet._meta.get_field('slug').max_length
        instance.slug = orig = slugify_pcat(instance.titre, max_length)

        for x in itertools.count(1):
            if not Projet.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = userProfile

        instance.save(sendMail)

        return instance


class ProjetChangeForm(forms.ModelForm):

    class Meta:
        model = Projet
        fields = ['asso', 'categorie', 'coresponsable', 'titre', 'contenu', 'tags', 'lien_document', 'start_time', 'estArchive']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
              'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }


class ProjetForm(forms.ModelForm):
    asso = forms.ModelChoiceField(queryset=Asso.objects.all(), required=True,
                              label="Projet public ou réservé aux adhérents de l'asso :", )
    class Meta:
        model = Projet
        fields = ['asso', 'categorie', 'coresponsable', 'titre', 'contenu', 'statut', 'tags',  'start_time']
        widgets = {
        'contenu': SummernoteWidget(),
              'start_time':forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
              'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def __init__(self, request, *args, **kwargs):
        super(ProjetForm, self).__init__(*args, **kwargs)
        self.fields['contenu'].strip = False
        self.fields["asso"].choices = [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if request.user.estMembre_str(x.abreviation)]

    def save(self, userProfile, sendMail=True):
        instance = super(ProjetForm, self).save(commit=False)

        max_length = Projet._meta.get_field('slug').max_length
        instance.slug = orig = slugify_pcat(instance.titre, max_length)

        for x in itertools.count(1):
            if not Projet.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = userProfile

        instance.save(sendMail)

        return instance


class FicheProjetForm(forms.ModelForm):
    class Meta:
        model = FicheProjet
        exclude = ['date_creation', 'date_modification', 'projet' ]
        widgets = {
            "raison": SummernoteWidget(),
            "pourquoi_contexte": SummernoteWidget(),
            "pourquoi_motivation": SummernoteWidget(),
            "pourquoi_objectifs": SummernoteWidget(),
            "pour_qui": SummernoteWidget(),
            "par_qui": SummernoteWidget(),
            "avec_qui": SummernoteWidget(),
            "ou": SummernoteWidget(),
            "quand": SummernoteWidget(),
            "comment": SummernoteWidget(),
            "combien": SummernoteWidget(),
        }


    def save(self, projet):
        instance = super(FicheProjetForm, self).save(commit=False)
        instance.projet = projet
        instance.save()
        return instance

class FicheProjetChangeForm(forms.ModelForm):

    class Meta:
        model = FicheProjet
        exclude = ['date_creation', 'date_modification', 'projet' ]
        widgets = {
            "raison": SummernoteWidget(),
            "pourquoi_contexte": SummernoteWidget(),
            "pourquoi_motivation": SummernoteWidget(),
            "pourquoi_objectifs": SummernoteWidget(),
            "pour_qui": SummernoteWidget(),
            "par_qui": SummernoteWidget(),
            "avec_qui": SummernoteWidget(),
            "ou": SummernoteWidget(),
            "quand": SummernoteWidget(),
            "comment": SummernoteWidget(),
            "combien": SummernoteWidget(),
        }

class CommentProjetForm(forms.ModelForm):

    class Meta:
        model = CommentaireProjet
        exclude = ['projet','auteur_comm']

        widgets = {
                'commentaire': SummernoteWidgetWithCustomToolbar(),
            }

    def __init__(self, request, *args, **kwargs):
         super(CommentProjetForm, self).__init__(request, *args, **kwargs)
         self.fields['commentaire'].strip = False


class CommentaireProjetChangeForm(forms.ModelForm):
     commentaire = forms.CharField(required=False, widget=SummernoteWidget())

     class Meta:
         model = CommentaireProjet
         exclude = ['projet', 'auteur_comm']
         widgets = {
             'commentaire': SummernoteWidget(),
         }


class EvenementForm(forms.ModelForm):
    qs = Article.objects.filter(estArchive=False)
    article = forms.ModelChoiceField(queryset=qs.order_by('titre')) #forms.ChoiceField(choices=Article.objects.all())

    class Meta:
        model = Evenement
        fields = ['start_time', 'titre_even', 'article', ]
        widgets = {
            'start_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def save(self, request):
        instance = super(EvenementForm, self).save(commit=False)
        instance.auteur = request.user
        instance.save()
        return instance

class EvenementArticleForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = ['start_time', 'titre_even', ]
        widgets = {
            'start_time':forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def save(self, request, article):
        instance = super(EvenementArticleForm, self).save(commit=False)
        instance.article = article
        instance.auteur = request.user
        instance.save()
        return instance


class SalonArticleForm(forms.ModelForm):

    class Meta:
        model = Salon
        fields = ['titre', 'estPublic' ]

    def save(self, request, article):
        instance = super(SalonArticleForm, self).save(commit=False)
        instance.article = article
        instance.save()
        inscrit = InscritSalon(salon=instance, profil=request.user)
        inscrit.save()
        return instance

class AdresseArticleForm(forms.ModelForm):
    class Meta:
        model = AdresseArticle
        fields = ['titre', 'type_marqueur', 'infos']

        widgets = {
            'infos': SummernoteWidget(),
        }

    def save(self, article, adresse):
        instance = super(AdresseArticleForm, self).save(commit=False)
        instance.article = article
        instance.adresse = adresse
        instance.save()
        return instance

class AdresseArticleChangeForm(forms.ModelForm):
    class Meta:
        model = AdresseArticle
        fields = ['titre', 'type_marqueur', 'infos']

        widgets = {
            'infos': SummernoteWidget(),
        }

class DocumentPartageArticleForm(forms.ModelForm):
    class Meta:
        model = DocumentPartage
        fields = ['nom', ]

    def save(self, article):
        instance = super(DocumentPartageArticleForm, self).save(commit=False)

        max_length = DocumentPartage._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.nom)[:max_length]

        for x in itertools.count(1):
            if not DocumentPartage.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.article = article
        instance.save()
        return instance

class DocumentPartageArticleModifierForm(forms.ModelForm):
    class Meta:
        model = DocumentPartage
        fields = ['nom', ]

class TodoArticleForm(forms.ModelForm):
    class Meta:
        model = TodoArticle
        fields = ['titre', 'description' ]

    def save(self, article):
        instance = super(TodoArticleForm, self).save(commit=False)

        max_length = TodoArticle._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not TodoArticle.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.article = article
        instance.save()
        return instance


class TodoArticleChangeForm(forms.ModelForm):
    class Meta:
        model = TodoArticle
        fields = ['titre', 'description']

class ReunionArticleForm(forms.ModelForm):

    class Meta:
        model = Reunion
        fields = ['categorie', 'titre', 'description', 'start_time']
        widgets = {
            'contenu': SummernoteWidget(),
            'start_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def save(self, auteur, article):
        instance = super(ReunionArticleForm, self).save(commit=False)
        max_length = DocumentPartage._meta.get_field('slug').max_length
        instance.slug = orig = slugify_pcat(instance.titre, max_length)

        for x in itertools.count(1):
            if not Reunion.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.article = article
        instance.auteur = auteur
        instance.asso = article.asso
        instance.save()
        return instance


class AssocierReunionArticleForm(forms.Form):
    reunion = forms.ModelChoiceField(queryset=Reunion.objects.order_by('-start_time'), required=True,
                              label="Réunion à associer à l'article", )

class ArticleLiensForm(forms.ModelForm):

    class Meta:
        model = ArticleLiens
        fields = ['type_lien']

    def save(self, auteur, article, article_lie):
        instance = super(ArticleLiensForm, self).save(commit=False)
        if article_lie and article != article_lie:
            instance.article = article
            instance.article_lie = article_lie
            instance.auteur = auteur
            instance.save()
            return instance
        else:
            return None

class Article_rechercheForm(forms.ModelForm):

    class Meta:
        model = Article_recherche
        fields = ("article", )
        widgets = {
            'article': autocomplete.ModelSelect2(url='blog:article-ac')
        }

    def save(self):
        instance = super(Article_rechercheForm, self).save()
        return instance

class ArticleLienProjetForm(forms.ModelForm):

    class Meta:
        model = ArticleLienProjet
        fields = ['type_lien']


    def save(self, auteur, article, projet_lie):
        instance = super(ArticleLienProjetForm, self).save(commit=False)
        instance.article = article
        instance.auteur = auteur
        instance.projet_lie = projet_lie
        instance.save()
        return instance


class Projet_rechercheForm(forms.ModelForm):

    class Meta:
        model = Projet_recherche
        fields = ("projet", )
        widgets = {
            'projet': autocomplete.ModelSelect2(url='blog:projet-ac')
        }

    def save(self):
        instance = super(Projet_rechercheForm, self).save()
        return instance