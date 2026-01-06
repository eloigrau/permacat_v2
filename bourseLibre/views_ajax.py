from .models import Produit, Salon, Favoris
from .forms import FavorisFormSansUrl
from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required
#from rest_framework import permissions
from .serializers import ProduitSerializer

class AnnoncesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = ProduitSerializer
    http_method_names = ['get',]
    queryset = Produit.objects.select_subclasses().order_by('-date_creation')

    def get_queryset(self):
        cle = self.request.query_params.get('cle')
        queryset = Produit.objects.filter(nom_produit="aaaaa")
        if cle == "thomas":
            queryset = Produit.objects.select_subclasses().order_by('-date_creation')

        return queryset


def ajax_annonces(request):
    cle = request.GET.get('cle')
    if not cle == "thomas":
        return render(request, 'ajax/annonces_list.html', {})
    qs = Produit.objects.filter(asso__slug="public").select_subclasses()
    return render(request, 'ajax/annonces_list.html', {"qs":qs})

def ajax_annonces(request):
    cle = request.GET.get('cle')
    if not cle == "thomas":
        return render(request, 'ajax/annonces_list.html', {})
    qs = Produit.objects.filter(asso__slug="public").select_subclasses()
    return render(request, 'ajax/annonces_list.html', {"qs":qs})

@login_required
def salonsParTag(request, tag):
    salons = Salon.objects.filter(tags__name__in=[tag, ]).distinct()
    return render(request, 'salon/salons_list_template_motcle.html', {'salons': salons, 'tag':tag})


@login_required
def ajax_ajouterFavoris(request):
    url_path = request.GET.get('url_path', None)
    nom = request.GET.get('nom', None)
    if nom is None:
        nb = Favoris.objects.filter(profil=request.user, nom__startswith='favoris').count()
        nom = 'favoris ' + str(nb)
    favoris, created = Favoris.objects.get_or_create(profil=request.user, url=url_path, nom=nom)
    if url_path:
        return redirect(url_path)
    return redirect("bienvenue")


def modal_ajouterFavoris(request):
    if request.user.is_authenticated:
        url_path = request.GET.get('url_path', None)
        if 'nom_favoris' in request.POST:
            nom = request.POST.get('nom_favoris', None)
        else:
            nb = Favoris.objects.filter(profil=request.user, nom__startswith='favoris').count()
            nom = 'favoris ' + str(nb)

        favoris, created = Favoris.objects.get_or_create(profil=request.user, url=url_path, nom=nom)
    else:
        url_path = request.url
    return redirect("bienvenue")
