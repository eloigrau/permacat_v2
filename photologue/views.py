from django.views.generic.dates import ArchiveIndexView, DateDetailView, DayArchiveView, MonthArchiveView, \
    YearArchiveView
from django.views.generic.detail import DetailView
from django.views.generic import ListView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.views.generic.edit import FormMixin
from .models import Photo, Album, Document
from django.shortcuts import render, redirect
from .forms import PhotoForm, AlbumForm, PhotoChangeForm, AlbumChangeForm, DocumentForm, DocumentChangeForm, Document_rechercheForm, Document_asso_rechercheForm, DocumentAssocierArticleForm
from .filters import DocumentFilter
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from bourseLibre.constantes import Choix as Choix_global
from bourseLibre.views import testIsMembreAsso
from blog.models import Article
from django.core.exceptions import PermissionDenied
from actstream import actions, action
from bourseLibre.models import Asso
from django.views.decorators.csrf import csrf_exempt
from actstream.models import following
from bourseLibre.models import Suivis
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from dal import autocomplete
from django.db.models import Q

from django.utils.text import slugify
import itertools
import os
from bourseLibre.views_base import DeleteAccess

class AlbumListView(ListView):
    paginate_by = 15

    def get_queryset(self):
        qs = Album.objects.on_site().exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre())

        if 'asso' in self.request.GET:
            qs = qs.filter(asso__slug=self.request.GET["asso"])

        return qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="albums")
        context['asso_list'] = self.request.user.getListeSlugsNomsAssoEtPublic()  # [(x.nom, x.slug) for x in Asso.objects.all().order_by("id") if self.request.user.est_autorise(x.slug)]

        if 'asso' in self.request.GET:
            self.request.session["asso_slug"] = self.request.GET["asso"]

        return context

class AlbumDetailView(DetailView):
    queryset = Album.objects.on_site().order_by("-date_creation")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.filter(album=self.object)
        return context


class AlbumDateView:
    queryset = Album.objects.on_site()
    date_field = 'date_creation'
    allow_empty = True


class AlbumDateDetailView(AlbumDateView, DateDetailView):
    pass


class AlbumArchiveIndexView(AlbumDateView, ArchiveIndexView):
    pass


class AlbumDayArchiveView(AlbumDateView, DayArchiveView):
    pass


class AlbumMonthArchiveView(AlbumDateView, MonthArchiveView):
    pass


class AlbumYearArchiveView(AlbumDateView, YearArchiveView):
    make_object_list = True

# Photo views.


class PhotoListView(ListView):
    paginate_by = 20

    def get_queryset(self):
        qs = Photo.objects.on_site()

        for nomAsso in Choix_global.slugsAsso:
            if not getattr(self.request.user, "adherent_" + nomAsso):
                qs = qs.exclude(albums__asso__slug=nomAsso)

        return  qs

class PhotoDetailView(DetailView):
    queryset = Photo.objects.on_site()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['album'] = self.object.get_album()
        return context


class DocListView(ListView, FormMixin):
    paginate_by = 50

    form_class = Document_rechercheForm

    # no get_context_data override

    def post(self, request, *args, **kwargs):
        # first construct the form to avoid using it as instance
        self.success_url = self.request.get_full_path()
        form = self.get_form()
        if form.is_valid():
            if form.cleaned_data["document"]:
                self.success_url = form.cleaned_data["document"].get_absolute_url()
        return HttpResponseRedirect(self.success_url)

    def get_queryset(self):

        if "reset_asso" in self.request.GET and "asso_slug" in self.request.session:
            del self.request.session["asso_slug"]
        if "asso" in self.request.GET:
            self.request.session["asso_slug"] = self.request.GET["asso"]
            qs = Document.objects.exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre()).filter(asso__slug=self.request.GET["asso"]).order_by("-date_creation")
        elif "asso_slug" in self.request.session:
            qs = Document.objects.exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre()).filter(asso__slug=self.request.session["asso_slug"]).order_by("-date_creation")
        else:
            qs = Document.objects.exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre()).order_by("-date_creation")

        return qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="documents")
        context['asso_list'] = self.request.user.getListeSlugsNomsAssoEtPublic()
            #[(x.slug, x.nom) for x in Asso.objects.all().order_by("id") if self.request.user.est_autorise(x.slug)]

        if 'asso' in self.request.GET:
            self.request.session["asso_slug"] = self.request.GET['asso']
            self.form = Document_rechercheForm(self.request.GET or None)
        else:
            self.form = Document_asso_rechercheForm(self.request.GET or None)

        context['form_document_recherche'] = self.get_form()

        return context

class PhotoDateView:
    queryset = Photo.objects.on_site()
    date_field = 'date_creation'
    allow_empty = True


class PhotoDateDetailView(PhotoDateView, DateDetailView):
    pass


class PhotoArchiveIndexView(PhotoDateView, ArchiveIndexView):
    pass


class PhotoDayArchiveView(PhotoDateView, DayArchiveView):
    pass


class PhotoMonthArchiveView(PhotoDateView, MonthArchiveView):
    pass


class PhotoYearArchiveView(PhotoDateView, YearArchiveView):
    make_object_list = True


@login_required
def ajouterPhoto(request, albumSlug):
    album = Album.objects.get(slug=albumSlug)
    asso = testIsMembreAsso(request, album.asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    if request.method == 'POST':
        form = PhotoForm(request, request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist("image")
            for photofile in images:
                f = Photo(image=photofile, )
                if not form.cleaned_data["title"]:
                    f.title = str(os.path.splitext(f.image.file.name)[0])
                else:
                    f.title = form.cleaned_data["title"]
                max_length = f._meta.get_field('slug').max_length
                f.slug = orig = slugify(f.title)[:max_length]

                for x in itertools.count(1):
                    if not Photo.objects.filter(slug=orig).exists():
                        break
                    orig = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)
                # Truncate the original slug dynamically. Minus 1 for the hyphen.
                f.slug = orig

                f.auteur = request.user
                f.save()
                album.photos.add(f)
            form.save(request)
           # form.save_m2m()
            return redirect(album.get_absolute_url())
    else:
        form = PhotoForm(request)
    return render(request, 'photologue/photo_ajouter.html', { "form": form, "album":album})



@login_required
def ajouterAlbum(request):
    form = AlbumForm(request, request.POST or None)
    if form.is_valid():
        album = form.save(request)
        suffix = "_" + album.asso.slug
        action.send(request.user, verb='album_nouveau' + suffix, action_object=album, url=album.get_absolute_url(),
                    description="a ajouté l'album: '%s'" % album.title)
        return redirect(album.get_absolute_url())
    return render(request, 'photologue/album_ajouter.html', { "form": form, })



# @login_required
class ModifierAlbum(UpdateView):
    model = Album
    form_class = AlbumChangeForm
    template_name_suffix = '_modifier'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Album.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        #self.object.date_modification = now()
        self.object.save()
        #if not self.object.estArchive:
        #    url = self.object.get_absolute_url()
        #    suffix = "_" + self.object.asso.slug
        #    action.send(self.request.user, verb='album_modifier'+suffix, action_object=self.object, url=url,
         #                description="a modifié l'album: '%s'" % self.object.titre)
        #envoi_emails_albumouprojet_modifie(self.object, "L'album " +  self.object.titre + "a été modifié", True)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ModifierAlbum, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if self.request.user.estMembre_str(x.slug)]

        return form

class SupprimerAlbum(DeleteAccess, DeleteView):
    model = Album
    success_url = reverse_lazy('photologue:album-list')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Album.objects.get(slug=self.kwargs['slug'])



# @login_required
class ModifierPhoto(UpdateView):
    model = Photo
    form_class = PhotoChangeForm
    template_name_suffix = '_modifier'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Photo.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        #self.object.date_modification = now()
        self.object.save()
        #if not self.object.estArchive:
        #    url = self.object.get_absolute_url()
        #    suffix = "_" + self.object.asso.slug
        #    action.send(self.request.user, verb='photo_modifier'+suffix, action_object=self.object, url=url,
        #                 description="a modifié la photo: '%s'" % self.object.titre)
        #envoi_emails_albumouprojet_modifie(self.object, "L'album " +  self.object.titre + "a été modifié", True)
        return HttpResponseRedirect(self.get_success_url())

    #def get_form(self,*args, **kwargs):
    #    form = super(ModifierPhoto, self).get_form(*args, **kwargs)
    #    form.fields["asso"].choices = sorted([(x.id, x.nom) for x in Asso.objects.all() if self.request.user.estMembre_str(x.slug)], key=lambda x:x[0])

        return form

class SupprimerPhoto(DeleteAccess, DeleteView):
    model = Photo
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Photo.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        return self.object.get_album_url()

@login_required
def telechargerDocument(request, slug):
    doc = get_object_or_404(Document, slug=slug)
    hit_count = HitCount.objects.get_for_object(doc)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)

    return render(doc.get_absolute_url())

@login_required
def ajouterDocument(request, article_slug=None):
    if article_slug and article_slug != 'None':
        article = Article.objects.get(slug=article_slug)
    else:
        article = None
    form = DocumentForm(request, article, request.POST or None, request.FILES or None)
    if form.is_valid():
        doc = form.save(request, article)
        if article :
            action.send(request.user, verb="article_modifier_" + doc.asso.slug, action_object=article, url=article.get_absolute_url(),
                        description="a ajouté le document: '%s'" % doc.titre)
        else:
            action.send(request.user, verb='document_nouveau' + "_" + doc.asso.slug, action_object=doc, url=doc.get_absolute_url(),
                            description="a ajouté le document: '%s'" % doc.titre)

        # Redirect to the document list after POST
        if article:
            return redirect(article)
        return HttpResponseRedirect(reverse_lazy("photologue:doc-list"))

    # Render list page with the documents and the form
    return render(request, 'photologue/document_ajouter.html', { "form": form})

@login_required
def associerDocumentArticle(request, doc_slug):
    doc = Document.objects.get(slug=doc_slug)
    form = DocumentAssocierArticleForm(request.session.get("asso_slug", None), request.POST)
    if form.is_valid():
        doc.article = form.cleaned_data["article"]
        doc.save()
        return HttpResponseRedirect(reverse_lazy("photologue:doc-list"))

    return render(request, 'photologue/document_associerArticle.html', {"form": form, 'doc': doc})


@login_required
def filtrer_documents(request):
    if request.GET:
        doc_list = Document.objects.exclude(asso__slug__in=request.user.getListeSlugsAssos_nonmembre())
    else:
        doc_list = Document.objects.none()
    f = DocumentFilter(request.GET, queryset=doc_list)
    #f=doc_list

    return render(request, 'photologue/document_filter.html', {'filter': f})

class SupprimerDocument(DeleteAccess, DeleteView):
    model = Document
    template_name_suffix = '_supprimer'

    def get_object(self):
        self.object = Document.objects.get(slug=self.kwargs['slug'])
        self.article = self.object.article
        return self.object

    def get_success_url(self):
        if self.article:
            return self.article.get_absolute_url()
        return reverse_lazy("photologue:doc-list")


class ModifierDocument(UpdateView):
    model = Document
    template_name_suffix = '_modifier'

    def get_object(self):
        self.object = Document.objects.get(slug=self.kwargs['slug'])
        self.article = self.object.article
        return self.object

    def get_form(self):
        return DocumentChangeForm(self.request, **self.get_form_kwargs())

    def get_success_url(self):
        if self.article:
            return self.article.get_absolute_url()
        return reverse_lazy("photologue:doc-list")


@login_required
@csrf_exempt
def suivre_documents(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='documents')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi, send_action=False)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only, send_action=False)
    return redirect('photologue:doc-list')


@login_required
@csrf_exempt
def suivre_albums(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='albums')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi, send_action=False)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only, send_action=False)
    return redirect('photologue:album-list')



class DocumentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        calc = len(self.q) > 1
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated or not calc:
            return Document.objects.none()

        if calc:
            #if "asso_slug" in self.request.session:
            #    qs = Article.objects.filter(titre__icontains=self.q, estArchive=False, asso__slug=self.request.session["asso_slug"]).exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre()).order_by("titre")
            #else:
                qs = Document.objects.exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre()).order_by("titre").filter(Q(titre__icontains=self.q) | Q(titre__istartswith=self.q))

        return qs

class DocumentAutocomplete_asso(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        calc = len(self.q) > 1
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated or not calc:
            return Document.objects.none()

        if calc:
            if "asso_slug" in self.request.session:
                qs = Document.objects.exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre(), estArchive=True).filter(Q(asso__slug=self.request.session["asso_slug"]) & (Q(titre__icontains=self.q) | Q(titre__istartswith=self.q))).order_by("titre")
            else:
                qs = Document.objects.exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre(), estArchive=True).filter(Q(titre__icontains=self.q) | Q(titre__istartswith=self.q)).order_by("titre")

        return qs