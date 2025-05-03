# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import  reverse
from .forms import Article_rechercheForm
from .models import Article, Commentaire, Projet, CommentaireProjet, Choix, ArticleLiens, ArticleLienProjet
from .views import get_tags_asso, get_articlesParTag
from django.contrib.auth.decorators import login_required
from bourseLibre.views import testIsMembreAsso
from ateliers.models import Atelier, CommentaireAtelier
from django.db.models import Q
from photologue.models import Document
import json
import itertools
from django.utils.safestring import mark_safe
from taggit.models import Tag

@login_required
def get_article_liens_ajax(request, asso):
    liens = ArticleLiens.objects.exclude(
        article__asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre()).filter(
        article__estArchive=False, article__asso__abreviation=asso).order_by('article')
    data_dict = {}
    i = 0
    for l in liens:
        if l.article_lie:
            if l.article.slug in data_dict.keys():
                if not {"nodeTo": l.article_lie.slug} in data_dict[l.article.slug]["adjacencies"]:
                    data_dict[l.article.slug]["adjacencies"].append(
                        {"nodeTo": l.article_lie.slug, })
            else:
                data_dict[l.article.slug] = {
                    "data": {"$color": "#416D9C", "$type": "circle", "$dim": 7},
                    "id": l.article.slug,
                    "name": formatTitre(l.article.titre),
                    "adjacencies": [
                        {"nodeTo": l.article_lie.slug,
                         # "data": {"$color": "#909291"}
                         },
                    ],
                }

    liens_projets = ArticleLienProjet.objects.exclude(
        projet_lie__asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre()).filter(
        projet_lie__estArchive=False, projet_lie__asso__abreviation=asso).order_by(
        'article')

    for l in liens_projets:
        if l.article:
            if l.article.slug in data_dict.keys():
                if not {"nodeTo": l.projet_lie.slug} in data_dict[l.article.slug]["adjacencies"]:
                    data_dict[l.article.slug]["adjacencies"].append(
                        {
                            "nodeTo": l.projet_lie.slug,
                         })
            else:
                titre = l.article.titre[:80].replace('"',"-").replace("'","-") if len(l.article.titre) > 75 else l.article.titre.replace('"',"-").replace("'","-")
                data_dict[l.article.slug] = {
                    "data": {"$color": "#00cc00", "$type": "square", "$dim": 7},
                    "id": l.article.slug,
                    "name": titre,
                    "adjacencies": [
                        {"nodeTo": l.projet_lie.slug,
                         # "data": {"$color": "#909291"}
                         },
                    ],
                }

    projets = Projet.objects.exclude(asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre(),
                                     estArchive=True).filter(asso__abreviation=asso)
    for p in projets:
        data_dict[p.slug] = {
            "data": {"$color": "#909291", "$type": "square", "$dim": 10},
            "id": p.slug,
            "name": p.titre[:80].replace('"',"-").replace("'","-"),
            "adjacencies": [
            ],
        }

    data_json = json.dumps(list(data_dict.values()), ensure_ascii=False)
    #return JsonResponse(list(data_dict.values()), safe=False, json_dumps_params={'ensure_ascii': False})
    return data_json

@login_required
def voir_articles_liens(request, asso):
    if not request.user.statutMembre_asso(asso):
        return HttpResponseForbidden()


    data_json = get_article_liens_ajax(request, asso)
    return render(request, 'blog/visu/voir_articlesliens_jit.html',{"data_json":data_json, "asso_abreviation":asso})

def formatTitre(titre):
    return titre[:100].replace('"',"-")#.replace("'","-")

class Noeuds():
    diconoeuds = {}
    listeLiens = []
    categories_id = {}
    ateliers_id = {}
    document_id = {}
    projet_id = {}

    def __init__(self, asso_abreviation, lienDossierArticles=True, projetAuCentre=False, categorieAuCentre=True):
        self.asso = asso_abreviation
        self.rayon = {"article":10, "categorie":20, "projet":30, "centre":1, "atelier":5, "document":5}
        self.ajouterNoeud(999999, "Articles", "group", reverse("blog:index_asso", kwargs={"asso":self.asso}), "centre" )
        self.lienDossierArticles = lienDossierArticles
        self.projetAuCentre = projetAuCentre
        self.categorieAuCentre = categorieAuCentre

    def get_categorie_id(self, cat):
        if not cat in self.categories_id:
            self.categories_id[cat] = 2000000 + len(self.categories_id)
        return self.categories_id[cat]

    def get_projet_id(self, cat):
        if not cat in self.projet_id:
            self.projet_id[cat] = 1000000 + len(self.projet_id)
        return self.projet_id[cat]

    def get_atelier_id(self, cat):
        if not cat in self.ateliers_id:
            self.ateliers_id[cat] = 3000000 + len(self.ateliers_id)
        return self.ateliers_id[cat]

    def get_document_id(self, cat):
        if not cat in self.ateliers_id:
            self.document_id[cat] = 4000000 + len(self.document_id)
        return self.document_id[cat]


    def get_dico_d3(self):
        return {
        "links": self.listeLiens,
         "nodes": [{"id": k,"name":v["name"],"group":v["group"],"url":v["url"], "rayon":self.rayon[v["type_noeud"]]} for k, v in self.diconoeuds.items()]
        }

    def ajouterLien(self, source_id, target_id, type_lien):
        #if not any()
        self.listeLiens.append({"source":source_id, "target":target_id,"type":type_lien})

    def ajouterNoeud(self, noeud_id, nom, group, url, type_noeud):
        if not noeud_id in self.diconoeuds.keys():
            self.diconoeuds[noeud_id]={"name": formatTitre(nom),
                                "url":url,
                                "group":group,
                               "type_noeud":type_noeud}
            return True
        return False

    def ajouterNoeudArticle(self, art):
        return self.ajouterNoeud(art.id, "Article : " + formatTitre(art.titre), art.categorie, art.get_absolute_url(), "article")

    def ajouterNoeudProjet(self, proj):
        id = self.get_projet_id(proj.id)
        cree = self.ajouterNoeud(id, "Projet : " + formatTitre(proj.titre), "Projet", proj.get_absolute_url(), "projet")
        if cree and self.projetAuCentre:
            self.ajouterLien(id, 999999,  type_lien="projet")
        return id

    def ajouterNoeudAtelier(self, a):
        id = self.get_atelier_id(a.id)
        cree = self.ajouterNoeud(noeud_id=id,
                          nom="Atelier : " + formatTitre(a.titre),
                          group="atelier",
                          url=a.get_absolute_url(),
                          type_noeud="atelier")
        if cree:
            self.ajouterNoeudArticle(a.article)
        return id

    def ajouterNoeudDocument(self, doc):
        id = self.get_document_id(doc.id)
        cree = self.ajouterNoeud(noeud_id=id,
                          nom="Document : " + formatTitre(doc.titre),
                          group="document",
                          url=doc.get_absolute_url(),
                          type_noeud="document")
        self.ajouterNoeudArticle(doc.article)
        return id

    def ajouterNoeudCategorie(self, art):
        id = self.get_categorie_id(art.categorie)
        cree = self.ajouterNoeud(id,
                          "Dossier : " + art.get_categorie_display(),
                          art.categorie,
                          reverse('blog:index_asso', kwargs={"asso": self.asso + "?categorie=" + art.categorie}),
                          "categorie")
        self.ajouterNoeudArticle(art)
        if cree and self.categorieAuCentre:
            self.ajouterLien(id, 999999, "centre")

        return id
    def ajouterNoeudsEtLiens_articles(self, art1, art2, type_lien):
        self.ajouterNoeudArticle(art1)
        self.ajouterNoeudArticle(art2)
        self.ajouterLien(art2.id, art1.id, type_lien)

    def ajouterNoeudsEtLiens_projet(self, article, proj2):
        self.ajouterNoeud(article.id, "Article : " + article.titre, article.categorie, article.get_absolute_url(), "article")
        id = self.ajouterNoeudProjet(proj2)
        self.ajouterLien(id, article.id,  type_lien="projet")

    def ajouterNoeudsEtLiens_projet_centre(self, article, proj2):
        self.ajouterNoeudArticle(article)
        id = self.ajouterNoeudProjet(proj2)
        self.ajouterLien(id, article.id, type_lien="projet")

    def ajouterLienArticleCategorie(self, art):
        if art:
            id = self.ajouterNoeudCategorie(art)
            self.ajouterLien(art.id, id, "dossier")

    def ajouterLienArticleDocumentsAteliers(self, art):
        for a in Atelier.objects.filter(article=art):
            id_at = self.ajouterNoeudAtelier(a)
            self.ajouterLien(id_at, art.id,  "atelier")
        for a in Document.objects.filter(article=art):
            id_at = self.ajouterNoeudDocument(a)
            self.ajouterLien(id_at, art.id, "document")


@login_required
def get_articles_asso_d3_network(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    articles = Article.objects.exclude(asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre()) \
                                .filter(estArchive=False, asso=asso)

    noeuds = Noeuds(asso_abreviation)
    for art in articles: #parcourt des articles de l'asso non archives
        # for tag in art.tags.all(): #on parcourt les tags de l'article
        #     art_tags = get_articlesParTag(asso, tag).filter(estArchive=False)# pour chaque tag on recupere les articles tagges pareil
        #     if len(art_tags) > 1: #si plus de 2 articles,
        #         for a in art_tags: # on parcourt les articles tagges
        #             noeuds.ajouterNoeudsEtLiens_articles(a, art, type_lien="tags")

        for liens in (ArticleLiens.objects.exclude(article__asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre()) \
                .filter(Q(article_lie__estArchive=False) & (Q(article=art) | Q(article_lie=art)))):
            if liens.article_lie and liens.article:
                noeuds.ajouterNoeudsEtLiens_articles(liens.article, liens.article_lie, type_lien="liens")

        for liens in ArticleLienProjet.objects.exclude(
            projet_lie__asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre()).filter(
            projet_lie__estArchive=False, projet_lie__asso=asso, article=art):
            noeuds.ajouterNoeudsEtLiens_projet(art, liens.projet_lie)

        noeuds.ajouterLienArticleCategorie(art)
        noeuds.ajouterLienArticleDocumentsAteliers(art)

    return JsonResponse(noeuds.get_dico_d3(), safe=True)

@login_required
def get_articles_asso_d3_network_dossier(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    articles = Article.objects.exclude(asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre()).filter(
                                       estArchive=False, asso=asso)
    noeuds = Noeuds(asso_abreviation, )
    for art in articles:
        noeuds.ajouterLienArticleCategorie(art)
        noeuds.ajouterLienArticleDocumentsAteliers(art)

    return JsonResponse(noeuds.get_dico_d3(), safe=True)


@login_required
def get_articles_asso_d3_network_projet(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    noeuds = Noeuds(asso_abreviation, lienDossierArticles=False, categorieAuCentre=False, projetAuCentre=True)
    for liens in ArticleLienProjet.objects.exclude(
        projet_lie__asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre()).filter(
        projet_lie__estArchive=False, projet_lie__asso=asso, article__asso=asso):
        noeuds.ajouterNoeudsEtLiens_projet_centre(liens.article, liens.projet_lie)

        noeuds.ajouterLienArticleDocumentsAteliers(liens.article)

    return JsonResponse(noeuds.get_dico_d3(), safe=True)

@login_required
def get_articles_asso_d3_hierar_dossier(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    articles = Article.objects.exclude(asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre()).filter(
                                       estArchive=False, asso=asso)

    categorie = list(set([(v, Choix.get_categorie_from_id(v)) for v in articles.values_list('categorie', flat=True).distinct()]))



    dico = {"name":"Par Dossier : " + asso.nom, "children":[]}
    for cat, nom in categorie: #parcourt des articles de l'asso non archives
        dico["children"].append({
            "name":nom,
            "nb_comm": 0,
            "couleur": Choix.couleurs_lien["categorie"],
            "url":"" ,#reverse('blog:index_asso', kwargs={"asso":asso.abreviation + "?categorie=" + cat}),
            "type": "dossier",
            "children": [{
                    "nb_comm":Commentaire.objects.filter(article=art).count(),
                    "name": formatTitre(art.titre),
                    "url":art.get_absolute_url(),
                    "couleur": Choix.couleurs_lien["article"] ,
                    "type": "article_epingle" if art.estEpingle else "article",
                    "children":[{
                        "nb_comm":CommentaireAtelier.objects.filter(atelier__article=art).count()
                        if isinstance(atelier, Atelier) else 0,
                        "name":"Atelier : " + formatTitre(atelier.titre)
                        if isinstance(atelier, Atelier) else "Document : " + formatTitre(atelier.titre),
                        "couleur": Choix.couleurs_lien["atelier"]
                        if isinstance(atelier, Atelier) else Choix.couleurs_lien["document"],
                        "url":atelier.get_absolute_url(),
                        "type": "atelier" if isinstance(atelier, Atelier) else "document",
                        }for atelier in itertools.chain(Atelier.objects.filter(article=art), Document.objects.filter(article=art),) ]
                    }for art in articles.filter(categorie=cat)]
            })


    return JsonResponse(dico, safe=True)

@login_required
def get_articles_asso_d3_hierar_dossier_simple(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    articles = Article.objects.exclude(asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre()).filter(
                                       estArchive=False, asso=asso)

    categorie = list(set([(v, Choix.get_categorie_from_id(v)) for v in articles.values_list('categorie', flat=True).distinct()]))



    dico = {"name":"Par Dossier : " + asso.nom, "children":[]}
    for cat, nom in categorie: #parcourt des articles de l'asso non archives
        dico["children"].append({
            "name":nom,
            "nb_comm": 0,
            "couleur": Choix.couleurs_lien["categorie"],
            "url":"" ,#reverse('blog:index_asso', kwargs={"asso":asso.abreviation + "?categorie=" + cat}),
            "type": "dossier",
            "children": [{
                    "nb_comm":Commentaire.objects.filter(article=art).count(),
                    "name": formatTitre(art.titre),
                    "url":art.get_absolute_url(),
                    "couleur": Choix.couleurs_lien["article"] ,
                    "type": "article_epingle" if art.estEpingle else "article",
                    "children": None
                    }for art in articles.filter(categorie=cat)]
            })


    return JsonResponse(dico, safe=True)
@login_required
def get_articles_asso_d3_hierar_projet(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)
    dico = {"name":"Par Projet : " + asso.nom, "children":[]}
    liste_liens = ArticleLienProjet.objects.exclude(
        projet_lie__asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre()).filter(
        projet_lie__estArchive=False, projet_lie__asso=asso, article__asso=asso).order_by('projet_lie__titre')

    projets = Projet.objects.exclude(
        asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre()).filter(
        estArchive=False, asso=asso)


    for proj in projets:
        dico["children"].append({
            "name":formatTitre(proj.titre),
            "url":proj.get_absolute_url(),
            "nb_comm":CommentaireProjet.objects.filter(projet=proj).count(),
            "couleur": Choix.couleurs_lien["projet"] ,
            "type": "projet",
            "children": [{
                    "name":formatTitre(lien.article.titre),
                    "url":lien.article.get_absolute_url(),
                    "nb_comm":Commentaire.objects.filter(article=lien.article).count(),
                    "couleur": Choix.couleurs_lien["article"] ,
                    "type": "article_epingle" if lien.article.estEpingle else "article",
                    "children":[{
                        "nom":atelier.slug,
                        "nb_comm":CommentaireAtelier.objects.filter(atelier__article=lien.article).count()
                            if isinstance(atelier, Atelier) else 0,
                        "name":"Atelier : " + formatTitre(atelier.titre)
                            if isinstance(atelier, Atelier) else "Document : " + formatTitre(atelier.titre) ,
                        "url":atelier.get_absolute_url(),
                        "couleur": Choix.couleurs_lien["atelier"]
                            if isinstance(atelier, Atelier) else Choix.couleurs_lien["document"],
                        "type": "atelier" if isinstance(atelier, Atelier) else "document",
                        }for atelier in itertools.chain(Atelier.objects.filter(article=lien.article), Document.objects.filter(article=lien.article),) ]
                    }for lien in liste_liens.filter(projet_lie=proj).distinct()]
            })


    return JsonResponse(dico, safe=True)


@login_required
def get_articles_asso_d3_hierar_tags(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)
    dico = {"name":"Par Tag : " + asso.nom, "children":[]}
    set(list(Article.objects.filter(asso=asso, estArchive=False).order_by('tags__name').values_list('tags',
                                                                                                    flat=True).distinct()))
    tags_asso = get_tags_asso(request, asso)
    for tag in Tag.objects.filter(id__in=tags_asso).order_by('name'):
        dico["children"].append({
            "name":tag.name,
            "url":"",
            "nb_comm":None,
            "couleur": Choix.couleurs_lien["tags"] ,
            "type": "tags",
            "children": [{
                    "name":formatTitre(article.titre),
                    "url":article.get_absolute_url(),
                    "nb_comm":Commentaire.objects.filter(article=article).count(),
                    "couleur": Choix.couleurs_lien["article"] ,
                    "type": "article_epingle" if article.estEpingle else "article",
                    "children":[{
                        "nom":atelier.slug,
                        "nb_comm":CommentaireAtelier.objects.filter(atelier__article=article).count()
                            if isinstance(atelier, Atelier) else 0,
                        "name":"Atelier : " + formatTitre(atelier.titre)
                            if isinstance(atelier, Atelier) else "Document : " + formatTitre(atelier.titre) ,
                        "url":atelier.get_absolute_url(),
                        "couleur": Choix.couleurs_lien["atelier"]
                            if isinstance(atelier, Atelier) else Choix.couleurs_lien["document"],
                        "type": "atelier" if isinstance(atelier, Atelier) else "document",
                        }for atelier in itertools.chain(Atelier.objects.filter(article=article), Document.objects.filter(article=article),) ]
                    }for article in get_articlesParTag(asso, tag).filter(estArchive=False)]
            })


    return JsonResponse(dico, safe=True)
@login_required
def get_articles_asso_d3_bubble(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    articles = Article.objects.exclude(asso__abreviation__in=request.user.getListeAbreviationsAssos_nonmembre(),
                                       estArchive=True).filter(asso=asso)

    #dico = list(set(["article."+ v['categorie'] for v in articles.values('categorie').distinct()]))
    #dico += ["article." + art.categorie + "." + art.slug + ",100" for art in articles]

    #dico = ["article." + art.categorie + "." + art.slug + ",100" for art in articles]
    dico = [{"type": "article",
             "group": art.categorie,
             "id": art.id,
             "name": art.slug.replace("-", " "),
             "value": 30, #HitCount.objects.get_for_object(art).hits,
             "url": mark_safe(art.get_absolute_url())}
            for art in articles]

    asso = "public"
    if "asso_abreviation" in request.session:
        asso = request.session["asso_abreviation"]

    groupes = set(articles.values_list("categorie", flat=True).distinct())

    dico += [{"type":"categorie",
              "group": g,
              "id": i + 1000000,
              "name": Choix.get_categorie_from_id(g),
              "value": 10,
              "url" : reverse('blog:index_asso', kwargs={"asso":asso}) + "?categorie=" + g
              } for i, g in enumerate(groupes)]
    #for art in articles: #parcourt des articles de l'asso non archives
   #     dico = "article." + art.categorie + "." + art.slug

    return JsonResponse(dico, safe=False)


@login_required
def voir_articles_liens_d3(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    form_article_recherche = Article_rechercheForm(request.POST or None)
    if form_article_recherche.is_valid() and form_article_recherche.cleaned_data['article']:
        return HttpResponseRedirect(form_article_recherche.cleaned_data['article'].get_absolute_url())

    return render(request, 'blog/visu/voir_articlesliens_d3.html',{"form_article_recherche":form_article_recherche, "asso_abreviation":asso.abreviation})

@login_required
def voir_articles_liens_d3_network(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    form_article_recherche = Article_rechercheForm(request.POST or None)
    if form_article_recherche.is_valid() and form_article_recherche.cleaned_data['article']:
        return HttpResponseRedirect(form_article_recherche.cleaned_data['article'].get_absolute_url())

    return render(request, 'blog/visu/voir_articlesliens_d3_network.html',{"form_article_recherche":form_article_recherche, "asso_abreviation":asso.abreviation})


@login_required
def voir_articles_liens_d3_network_dossier(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    form_article_recherche = Article_rechercheForm(request.POST or None)
    if form_article_recherche.is_valid() and form_article_recherche.cleaned_data['article']:
        return HttpResponseRedirect(form_article_recherche.cleaned_data['article'].get_absolute_url())

    return render(request, 'blog/visu/voir_articlesliens_d3_network_dossier.html',{"form_article_recherche":form_article_recherche, "asso_abreviation":asso.abreviation})

@login_required
def voir_articles_liens_d3_network_projet(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    form_article_recherche = Article_rechercheForm(request.POST or None)
    if form_article_recherche.is_valid() and form_article_recherche.cleaned_data['article']:
        return HttpResponseRedirect(form_article_recherche.cleaned_data['article'].get_absolute_url())

    return render(request, 'blog/visu/voir_articlesliens_d3_network_projet.html',{"form_article_recherche":form_article_recherche, "asso_abreviation":asso.abreviation})

@login_required
def voir_articles_liens_d3_bubble(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    form_article_recherche = Article_rechercheForm(request.POST or None)
    if form_article_recherche.is_valid() and form_article_recherche.cleaned_data['article']:
        return HttpResponseRedirect(form_article_recherche.cleaned_data['article'].get_absolute_url())

    return render(request, 'blog/visu/voir_articlesliens_d3_bubble.html',{"form_article_recherche":form_article_recherche, "asso_abreviation":asso.abreviation})


@login_required
def voir_articles_liens_d3_tree(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    form_article_recherche = Article_rechercheForm(request.POST or None)
    if form_article_recherche.is_valid() and form_article_recherche.cleaned_data['article']:
        return HttpResponseRedirect(form_article_recherche.cleaned_data['article'].get_absolute_url())

    return render(request, 'blog/visu/voir_articlesliens_d3_tree.html',{"form_article_recherche":form_article_recherche, "asso_abreviation":asso.abreviation})


@login_required
def voir_articles_liens_d3_tree2(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    form_article_recherche = Article_rechercheForm(request.POST or None)
    if form_article_recherche.is_valid() and form_article_recherche.cleaned_data['article']:
        return HttpResponseRedirect(form_article_recherche.cleaned_data['article'].get_absolute_url())

    return render(request, 'blog/visu/voir_articlesliens_d3_tree_vok.html',{"form_article_recherche":form_article_recherche, "asso_abreviation":asso.abreviation})


@login_required
def voir_articles_liens_d3_tree_indented_dossier(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    form_article_recherche = Article_rechercheForm(request.POST or None)
    if form_article_recherche.is_valid() and form_article_recherche.cleaned_data['article']:
        return HttpResponseRedirect(form_article_recherche.cleaned_data['article'].get_absolute_url())

    return render(request, 'blog/visu/voir_articlesliens_d3_tree_indented_dossier.html',{"form_article_recherche":form_article_recherche, "asso_abreviation":asso.abreviation})



@login_required
def voir_articles_liens_d3_tree_indented_projet(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    form_article_recherche = Article_rechercheForm(request.POST or None)
    if form_article_recherche.is_valid() and form_article_recherche.cleaned_data['article']:
        return HttpResponseRedirect(form_article_recherche.cleaned_data['article'].get_absolute_url())

    return render(request, 'blog/visu/voir_articlesliens_d3_tree_indented_projet.html',{"form_article_recherche":form_article_recherche, "asso_abreviation":asso.abreviation})


@login_required
def voir_articles_liens_d3_tree_indented_tags(request, asso_abreviation):
    asso = testIsMembreAsso(request, asso_abreviation)

    form_article_recherche = Article_rechercheForm(request.POST or None)
    if form_article_recherche.is_valid() and form_article_recherche.cleaned_data['article']:
        return HttpResponseRedirect(form_article_recherche.cleaned_data['article'].get_absolute_url())

    return render(request, 'blog/visu/voir_articlesliens_d3_tree_indented_tags.html',{"form_article_recherche":form_article_recherche, "asso_abreviation":asso.abreviation})

