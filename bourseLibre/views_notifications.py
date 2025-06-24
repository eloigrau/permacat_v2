from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from actstream.models import Action, any_stream, Follow
from bourseLibre.constantes import Choix as Choix_global
from bourseLibre.models import Profil, Asso, Conversation, Message
from django.utils.timezone import now
from itertools import chain
from .forms import nouvelleDateForm
from datetime import datetime, timedelta
from pytz import UTC as utc
from hitcount.models import HitCount, Hit
import pytz

@login_required
def getNotifications(request, nbNotif=15, orderBy="-timestamp"):
    tampon = nbNotif * 5
    dateMin = (datetime.now() - timedelta(days=15)).replace(tzinfo=utc)
    articles = Action.objects.filter(Q(timestamp__gt=dateMin) & Q(verb__startswith='article_')).order_by(orderBy)
    projets = Action.objects.filter(Q(timestamp__gt=dateMin) & Q(verb__startswith='projet_')).order_by(orderBy)
    offres = Action.objects.filter(Q(timestamp__gt=dateMin) & Q(verb__startswith='ajout_offre')).order_by(orderBy)
    suffrages = Action.objects.filter(Q(timestamp__gt=dateMin) & Q(verb__startswith='suffrage_')).order_by(orderBy)
    albums = Action.objects.filter(Q(timestamp__gt=dateMin) & Q(verb__startswith='album_')).order_by(orderBy)
    documents = Action.objects.filter(Q(timestamp__gt=dateMin) & Q(verb__startswith='document_')).order_by(orderBy)
    suppressions = Action.objects.filter(Q(timestamp__gt=dateMin) & Q(verb__startswith='suppression_article')).order_by(orderBy)
    jardins = Action.objects.none()
    conversations = Action.objects.none()

    for nomAsso in Choix_global.slugsAsso:
        if not getattr(request.user, "adherent_" + nomAsso):
            articles = articles.exclude(Q(verb__icontains=nomAsso))
            projets = projets.exclude(Q(verb__icontains=nomAsso))
            offres = offres.exclude(Q(verb__icontains=nomAsso))
            albums = albums.exclude(Q(verb__icontains=nomAsso))
            documents = documents.exclude(Q(verb__icontains=nomAsso))
            suppressions = suppressions.exclude(Q(verb__icontains=nomAsso))
        else:
            if nomAsso == 'jp':
                jardins = Action.objects.filter(Q(verb__startswith='jardins_'))

    salons = Action.objects.filter(Q(timestamp__gt=dateMin) & (Q(verb='envoi_salon_Public') |
                                                               Q(verb__startswith='creation_salon_public') |
                                                               Q(verb='envoi_salon_public'))).order_by(orderBy)
    salons = salons | Action.objects.filter(Q(timestamp__gt=dateMin) &
            (Q(verb__startswith="envoi_salon_public")| Q(verb__startswith="envoi_salon", description__contains=request.user.username) |
            Q(verb__startswith="invitation_salon", description__contains=request.user.username)))
    #conversations = Action.objects.filter(Q(timestamp__gt=dateMin) & Q(verb__startswith="envoi_salon_prive") &
     #                                     Q(description__contains=request.user.username))
    inscription = Action.objects.filter(Q(timestamp__gt=dateMin, verb__startswith='inscript')).order_by(orderBy)
    mentions = Action.objects.filter(Q(timestamp__gt=dateMin, verb='mention_' + request.user.username)).order_by(orderBy)
    fiches = Action.objects.filter(Q(timestamp__gt=dateMin, verb__startswith='fiche')).order_by(orderBy)
    ateliers = Action.objects.filter(Q(timestamp__gt=dateMin, verb__startswith='atelier')).order_by(orderBy)

    salons = salons.distinct().order_by(orderBy)[:tampon]
    #conversations = conversations.distinct().order_by(orderBy)[:tampon]
    articles = articles.distinct().order_by(orderBy)[:tampon]
    projets = projets.distinct().order_by(orderBy)[:tampon]
    offres = offres.distinct().order_by(orderBy)[:tampon]
    suffrages = suffrages.distinct().order_by(orderBy)[:tampon]
    albums = albums.distinct().order_by(orderBy)[:tampon]
    documents = documents.distinct().order_by(orderBy)[:tampon]
    suppressions = suppressions.distinct().order_by(orderBy)[:tampon]
    inscription = inscription.distinct().order_by(orderBy)[:tampon]
    mentions = mentions.distinct().order_by(orderBy)[:tampon]
    fiches = fiches.distinct().order_by(orderBy)[:tampon]
    ateliers = ateliers.distinct().order_by(orderBy)[:tampon]

    if jardins:
        jardins = jardins.distinct().order_by(orderBy)[:tampon]

    fiches = [art for i, art in enumerate(fiches) if i == 0 or not (art.description == fiches[i-1].description and art.actor == fiches[i-1].actor ) ][:nbNotif]
    ateliers = [art for i, art in enumerate(ateliers) if i == 0 or not (art.description == ateliers[i-1].description and art.actor == ateliers[i-1].actor ) ][:nbNotif]
    articles = [art for i, art in enumerate(articles) if i == 0 or not (art.description == articles[i-1].description  and art.actor == articles[i-1].actor)][:nbNotif]
    projets = [art for i, art in enumerate(projets) if i == 0 or not (art.description == projets[i-1].description and art.actor == projets[i-1].actor ) ][:nbNotif]
    salons = [art for i, art in enumerate(salons) if i == 0 or not (art.description == salons[i-1].description and art.actor == salons[i-1].actor ) ][:nbNotif]
    offres = [art for i, art in enumerate(offres) if i == 0 or not (art.description == offres[i-1].description and art.actor == offres[i-1].actor ) ][:nbNotif]
    albums = [art for i, art in enumerate(albums) if i == 0 or not (art.description == albums[i-1].description and art.actor == albums[i-1].actor ) ][:nbNotif]
    mentions = [art for i, art in enumerate(mentions) if i == 0 or not (art.description == mentions[i-1].description and art.actor == mentions[i-1].actor ) ][:nbNotif]
    #conversations = [art for i, art in enumerate(conversations) if i == 0 or not (art.description == conversations[i-1].description and art.actor == conversations[i-1].actor)][:nbNotif]

    if jardins:
        jardins = [art for i, art in enumerate(jardins) if i == 0 or not (art.description == jardins[i-1].description and art.actor == jardins[i-1].actor ) ][:nbNotif]
    documents = [art for i, art in enumerate(documents) if i == 0 or not (art.description == documents[i-1].description and art.actor == documents[i-1].actor ) ][:nbNotif]

    return salons, articles, projets, offres, conversations, fiches, ateliers, inscription, suffrages, albums, documents, mentions, jardins, suppressions

@login_required
def getNotificationsParDate(request, dateMinimum=None, orderBy="-timestamp"):
    if dateMinimum:
        dateMin = dateMinimum if dateMinimum.date() > datetime.now().date() - timedelta(
            days=30) else datetime.now().date() - timedelta(days=20)
    else:
        dateMin = (datetime.now() - timedelta(days=7)).replace(tzinfo=utc)

    actions = Action.objects.filter(Q(timestamp__gt=dateMin) & ( \
         Q(verb__startswith='article_') | Q(verb__startswith='projet_') |
         Q(verb__icontains='_public') | Q(verb__icontains='_Public') |
            Q(verb__startswith='fiche') | Q(verb__startswith='atelier') |
            Q(verb__startswith='jardins_') |
            Q(verb__startswith='document_') | Q(verb__startswith='album_') |
            Q(verb__startswith="envoi_salon_public") |
            Q(verb__startswith="envoi_salon", description__contains=request.user.username) |
            Q(verb__startswith="invitation_salon", description__contains=request.user.username) |
            Q(verb__startswith='inscription') |
            Q(verb__startswith='mention_' + request.user.username) |
            Q(verb__startswith='suppression' + request.user.username))).distinct().order_by(orderBy)

    query_exclude = Q()
    for nomAsso in request.user.getListeSlugsAssos_nonmembre():
        query_exclude = query_exclude & Q(verb__icontains="_" + nomAsso)
    actions.exclude(query_exclude)
    actions = [art for i, art in enumerate(actions[:200]) if i == 0 or not (art.description == actions[i-1].description and art.actor == actions[i-1].actor ) ]

    return actions



@login_required
def getNbNewNotifications_test(request):
    return len(getNotificationsParDate(request))

@login_required
def getNbNewNotifications_test2(request):
    try:
        dateLimite = datetime.now().date() - timedelta(days=7)
        dateMin = request.user.date_notifications.date() if request.user.date_notifications.date() > dateLimite else dateLimite

        actions = getNotificationsParDate(request, dateMinimum=dateMin)
    except:
        return 0

    return len(actions)

@login_required
def getNbNewNotifications(request):
    return len(getNotificationsParDate(request, dateMinimum=request.user.date_notifications))

@login_required
def getFavoris(request):
    return request.user.getFavoris()

@login_required
def notificationsParGroupe(request, dateMinimum=None, orderBy="-timestamp"):
    actions = []

    if dateMinimum:
        dateMin = dateMinimum if dateMinimum.date() > datetime.now().date() - timedelta(
            days=20) else (datetime.now() - timedelta(days=20)).replace(tzinfo=utc)
    else:
        dateMin = (datetime.now() - timedelta(days=20)).replace(tzinfo=utc)

    if "asso" in request.GET:
        request.session["asso_slug"] = request.GET["asso"]
        actions = Action.objects.filter(Q(timestamp__gt=dateMin, verb__contains=request.session["asso_slug"]) & ( \
             Q(verb__startswith='article')|Q(verb__startswith='projet_')|
             Q(verb__startswith='atelier')|Q(verb__startswith='jardins_')|
                Q(verb__startswith='documents_nouveau')|
             Q(verb__startswith='album_nouveau'))).distinct().order_by(orderBy)[:200]

    #actions = [art for i, art in enumerate(actions) if i == 0 or not (art.description == actions[i-1].description and art.actor == actions[i-1].actor ) ]

    context = {'actions':actions,
                'asso_list':  request.user.getListeSlugsNomsAssoEtPublic()  # [(x.nom, x.slug) for x in Asso.objects.all().order_by("id") if self.request.user.est_autorise(x.slug)]
    }
    return render(request, 'notifications/notificationsParGroupe.html', context)

def raccourcirTempsStr(date):
    new = date.replace("heures","h")
    new = new.replace("heure","h")
    new = new.replace("minutes","mn")
    new = new.replace("minute","mn")
    splitted = new.split(", ")
    if splitted:
        return splitted[0]
    return new

@login_required
def notifications_news_regroup(request):
    salons, articles, projets, offres, conversations, fiches, ateliers, inscriptions, suffrages, albums, documents, mentions, jardins, suppressions = getNotifications(request, nbNotif=500)

    dicoTexte = {}
    dicoTexte['dicoarticles'] = {}

    if "fromdate" in request.GET:
        dateMin = datetime.strptime(request.GET["fromdate"], '%d-%m-%Y').replace(tzinfo=utc)
        type_notif = "fromdate"
    else:
        date7jours = (datetime.now() - timedelta(days=15)).replace(tzinfo=utc)
        dateMin = request.user.date_notifications if request.user.date_notifications > date7jours else date7jours
        type_notif = "dateNotif"

    for action in articles:
        if dateMin < action.timestamp:
            try:
                #clef = "["+action.action_object.asso.nom+"] " + action.action_object.titre
                clef = action.action_object.get_logo_nomgroupe_html_taille(17) + " " + action.action_object.titre
            except:
                clef = action.action_object.titre
            if not clef in dicoTexte['dicoarticles']:
                dicoTexte['dicoarticles'][clef] = [action, ]
            else:
                dicoTexte['dicoarticles'][clef].append(action)

    htmlArticles = ""
    for titre_article, actions in dicoTexte['dicoarticles'].items():
        htmlArticles += "<li class='list-group-item'><a href='" + actions[0].data['url'] + "'>"
        htmlArticles += " <div class=''><span  style='font-variant: small-caps ;'>"
        htmlArticles += titre_article+"</span>"
        htmlArticles +=" </div><ul style='list-style-type:none'>"

        for action in actions :
            htmlArticles += "<li>"
            if action.description.startswith("a réagi"):
                if "discussion" in action.data and action.data['discussion'] != 'Discussion Générale':
                    htmlArticles += "(" + action.data['discussion'] + ") "
                htmlArticles += "commenté par " + str(action.actor)

            elif action.description.startswith("a ajout"):
                if action.description.startswith("a ajouté un article "):
                    htmlArticles += "créé par "+ str(action.actor)
                elif action.description.startswith("a ajouté une date"):
                    htmlArticles += str(action.actor) + " a ajouté une date"
                elif action.description.startswith("a ajouté un lieu"):
                    htmlArticles += str(action.actor) + " a ajouté un lieu"
                elif action.description.startswith("a ajouté un document partagé"):
                    htmlArticles += str(action.actor) + " a ajouté un document partagé"
                elif action.description.startswith("a ajouté un todo"):
                    htmlArticles += str(action.actor) + " a ajouté un todo"
                elif action.description.startswith("a ajouté le document"):
                    htmlArticles += str(action.actor) + " " + str(action.description)
                elif action.description.startswith("a ajouté un salon"):
                    htmlArticles += str(action.actor) + " a ajouté un salon"
                elif action.description.startswith("a ajouté une réunion"):
                    htmlArticles += str(action.actor) + "a ajouté une réunion"
                else:
                    htmlArticles += str(action.description)
            elif action.description.startswith("a modif"):
                htmlArticles += "modifié par "+ str(action.actor)
            elif action.description.startswith("a archiv"):
                htmlArticles += "archivé par " + str(action.actor)
            else:
                htmlArticles += " " + action.description
            htmlArticles += "&nbsp;&nbsp;<small> (il y a " + raccourcirTempsStr(action.timesince()) + ")</small></li>"

        htmlArticles += " </ul></a></li>"

    dicoTexte['dicoprojets'] = {}
    for action in projets:
        if dateMin < action.timestamp:
            clef = action.action_object.titre
            if not clef in dicoTexte['dicoprojets']:
                dicoTexte['dicoprojets'][clef] = [action, ]
            else:
                dicoTexte['dicoprojets'][clef].append(action)

    htmlProjets = ""
    for titre_projet, actions in dicoTexte['dicoprojets'].items():
        htmlProjets += "<li class='list-group-item'><a href='" + actions[0].data['url'] + "'>"
        htmlProjets += " <div  class='' ><spanstyle='font-variant: small-caps ;'>" + titre_projet
        if "(Jardins Partagés)" in actions[0].description:
            htmlProjets += "</span> (Jardins Partagés)"
        else:
            htmlProjets += "</span>"
        htmlProjets += " </div><ul style='list-style-type:none'>"

        for action in actions:
            htmlProjets += "<li>"
            if action.description.startswith("a réagi"):
                htmlProjets += "commenté par "
            elif action.description.startswith("a ajout"):
                htmlProjets += "créé par "
            elif action.description.startswith("a modif"):
                htmlProjets += "modifié par "
            else:
                htmlProjets += str(action.actor) + " " + action.description
            htmlProjets += str(action.actor) + "&nbsp;&nbsp;<small> (il y a " + raccourcirTempsStr(
                action.timesince()) + ")</small></li>"
        htmlProjets += " </ul></a></li>"

    dicoTexte['listinscriptions'] = []
    for action in inscriptions:
        if dateMin < action.timestamp:
            dicoTexte['listinscriptions'].append(action)


    dicoTexte['listautres'] = []
    for action in list(chain(suffrages, conversations, salons, offres, ateliers, fiches, albums, documents, mentions, jardins, suppressions)):
        if dateMin < action.timestamp:
            dicoTexte['listautres'].append(action)

    maintenant = now()
    request.user.date_notifications = maintenant
    request.user.save()
    #print("prooooj" + str(htmlProjets))
    return render(request, 'notifications/notifications_last2.html', {'type_notif':type_notif,'dico':dicoTexte, "htmlArticles":htmlArticles, "htmlProjets":htmlProjets, "dateMin":dateMin, "maintenant":maintenant})


@login_required
def notifications(request):
    salons, articles, projets, offres, conversations, fiches, ateliers, inscriptions, suffrages, albums, documents, mentions, jardins, suppressions = getNotifications(request)
    return render(request, 'notifications/notifications.html', {'salons': salons, 'articles': articles,'projets': projets, 'offres':offres, 'conversations':conversations, 'fiches':fiches, 'ateliers':ateliers, 'inscriptions':inscriptions, 'suffrages':suffrages})

@login_required
def notifications_news(request):
    actions = getNotificationsParDate(request)
    maintenant = now()
    #hit_count = HitCount.objects.all().order_by('-hit__created')[:10]
    return render(request, 'notifications/notifications_last.html', {'actions':actions, "maintenant":maintenant})


@login_required
def notificationsParDate(request):
    actions = getNotificationsParDate(request)
    return render(request, 'notifications/notificationsParDate.html', {'actions': actions, })

@login_required
def notificationsLues(request, temps=None):
    try:
        if temps:
            request.user.date_notifications = temps
        else:
            request.user.date_notifications = now()
    except:
        request.user.date_notifications = now()

    request.user.save()

    return redirect('notifications_news')

def getInfosJourPrecedent(request, nombreDeJours):
    timestamp_from = datetime.now().date() - timedelta(days=nombreDeJours)
    timestamp_to = datetime.now().date() - timedelta(days=nombreDeJours - 1)

    if request.user.adherent_pc:
        articles    = Action.objects.filter(Q(verb='article_nouveau_permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) |
                                            Q(verb='article_nouveau_Permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) |
                                            Q(verb='article_nouveau',timestamp__gte = timestamp_from, timestamp__lte = timestamp_to,))
        projets     = Action.objects.filter(Q(verb='projet_nouveau_permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) |
                                            Q(verb='projet_nouveau_Permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) |
                                            Q(verb='projet_nouveau', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
        offres      = Action.objects.filter(Q(verb='ajout_offre', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) | Q(verb='ajout_offre_permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) | Q(verb='ajout_offre_Permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
    else:
        articles    = Action.objects.filter(Q(verb='article_nouveau', timestamp__gte = timestamp_from, timestamp__lte = timestamp_to,) | Q(verb='article_modifier', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
        projets     = Action.objects.filter(Q(verb='projet_nouveau', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
        offres      = Action.objects.filter(Q(verb='ajout_offre', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
    fiches = Action.objects.filter(verb__startswith='fiche')
    albums = Action.objects.filter(verb__startswith='album')
    ateliers = Action.objects.filter(Q(verb__startswith='atelier')|Q(verb=''))
    conversations = (any_stream(request.user).filter(Q(verb='envoi_salon_prive', )) | Action.objects.filter(
        Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username)))

    articles = [art for i, art in enumerate(articles) if i == 0 or not (art.description == articles[i-1].description  and art.actor == articles[i-1].actor)]
    projets = [art for i, art in enumerate(projets) if i == 0 or not (art.description == projets[i-1].description and art.actor == projets[i-1].actor) ]
    offres = [art for i, art in enumerate(offres) if i == 0 or not (art.description == offres[i-1].description and art.actor == offres[i-1].actor) ]
    fiches = [art for i, art in enumerate(fiches) if i == 0 or not (art.description == fiches[i-1].description and art.actor == fiches[i-1].actor ) ]
    ateliers = [art for i, art in enumerate(ateliers) if i == 0 or not (art.description == ateliers[i-1].description and art.actor == ateliers[i-1].actor ) ]
    conversations = [art for i, art in enumerate(conversations) if i == 0 or not (art.description == conversations[i-1].description and art.actor == conversations[i-1].actor ) ]
    albums = [art for i, art in enumerate(albums) if i == 0 or not (art.description == albums[i-1].description and art.actor == albums[i-1].actor ) ]

    return articles, projets, offres, fiches, ateliers, conversations, albums

def getTexteJourPrecedent(nombreDeJour):
    if nombreDeJour == 0:
        return "Aujourd'hui"
    elif nombreDeJour == 1:
        return "Hier"
    elif nombreDeJour == 2:
        return "Avant-hier"
    else:
        return "Il y a " + str(nombreDeJour) + " jours"

@login_required
def dernieresInfos(request):
    info_parjour = []
    for i in range(15):
        info_parjour.append({"jour":getTexteJourPrecedent(i), "infos":getInfosJourPrecedent(request, i)})
    return render(request, 'notifications/notifications_news.html', {'info_parjour': info_parjour,})


@login_required
def changerDateNotif(request):
    form = nouvelleDateForm(request.POST or None, )
    if form.is_valid():
        date = form.cleaned_data['date']
        return redirect('/notifications/activite'+ "?fromdate=" + str(date.day) +"-" + str(date.month) + "-" + str(date.year))
        #return HttpResponseRedirect('notifications_news' + "?fromdate=" + date.day +"-" + date.month + "-" + date.year)
        #request.user.date_notifications = form.cleaned_data['date']
        #request.user.save()
        #return redirect('notifications_news')
    else:
        return render(request, 'notifications/date_notifs.html', {'form': form})

@login_required
def notif_cejour(request):
    date = datetime.now().date()
    return redirect('/notifications/activite'+ "?fromdate=" + str(date.day) +"-" + str(date.month) + "-" + str(date.year))

@login_required
def notif_hier(request):
    date = datetime.now().date() - timedelta(days=1)
    return redirect('/notifications/activite'+ "?fromdate=" + str(date.day) +"-" + str(date.month) + "-" + str(date.year))

@login_required
def notif_cettesemaine(request):
    date_ajd = datetime.now().date()
    date = date_ajd - timedelta(days=date_ajd.weekday())
    return redirect('/notifications/activite'+ "?fromdate=" + str(date.day) +"-" + str(date.month) + "-" + str(date.year))

@login_required
def notif_cemois(request):
    date_ajd = datetime.now().date()
    date = date_ajd - timedelta(days=date_ajd.day - 1)
    return redirect('/notifications/activite'+ "?fromdate=" + str(date.day) +"-" + str(date.month) + "-" + str(date.year))


@login_required
def voirDerniersArticlesVus(request):
    date_ajd = datetime.now().date()
    hit_count = Hit.objects.filter(created__gte=date_ajd - timedelta(days=33)).order_by('-created').distinct()
    dates = [date_ajd,  date_ajd - timedelta(days=date_ajd.weekday()),  date_ajd - timedelta(days=date_ajd.day - 1)]
    hit_count_nb = [hit_count.filter(created__gte=date).count() for date in dates]

    hit_count_nb.append(Profil.objects.filter(last_login__gte=date_ajd - timedelta(days=140)).count())
    liste = {}
    for i, x in enumerate(hit_count):
        if len(liste) < 15 and x.hitcount.content_object and not str(x.hitcount.content_object).startswith("visite_") :
            if not str(x.hitcount.content_object) in liste:
                liste[str(x.hitcount.content_object)] = [x.hitcount.content_object.get_absolute_url, [x.user, ]]
            else:
                nom = str(x.hitcount.content_object)
                if x.user not in liste[nom][1]:
                   # if len(liste[nom][1]) == 10:
                   #     liste[nom][1].append("...")
                   # elif len(liste[nom][1]) > 10:
                   #     pass
                   # else:
                    liste[str(nom)][1].append(x.user)
    #ht = {str(x.hitcount.content_object): [x.hitcount.content_object.get_absolute_url, x.user] for i, x in enumerate(hit_count) if x.hitcount.content_object}
    #liste = {x: y for i, (x, y) in enumerate(liste.items()) if i <15}
    hit_count_perso = Hit.objects.filter(user=request.user.id).order_by('-created').distinct()[:20]

    return render(request, 'notifications/notifications_visites.html', {'hit_count': liste, 'hit_count_perso': hit_count_perso, 'hit_count_nb':hit_count_nb})


@login_required
def nbDerniersMessages(request):
    date_messages = request.user.date_messages.astimezone(pytz.timezone("Europe/Paris"))
    date_limite = (datetime.now() - timedelta(days=30)).astimezone(pytz.timezone("Europe/Paris"))
    dateMin = date_messages if date_messages > date_limite else date_limite

    messages = Message.objects.exclude(auteur=request.user).filter(Q(date_creation__gt=dateMin) & (Q(conversation__profil1=request.user) | Q(conversation__profil2=request.user)))
    notifs = getNbNewNotifications(request)
        #Conversation.objects.filter(Q(date_dernierMessage__isnull=False, date_dernierMessage__gt=dateMin) & (Q(profil2__id=request.user.id) | Q(profil1__id=request.user.id)))
    dico = {"nb_messages": len(messages), "nb_notifs": notifs,
            #"dateMin": dateMin,"date_messages":date_messages,"maintenant":datetime.now().replace(tzinfo=utc),
            #"messages": [m.message for m in messages],
            #"dates": [m.date_creation for m in messages]
            #"listeConv":[(m.conversation.get_destinataire(request), m.conversation.get_absolute_url()) for m in messages]
            }

    return JsonResponse(dico, safe=True)