# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from actstream.models import Action, Follow
from .models import Profil, Adhesion_asso, Suivis, Adresse, InscriptionNewsletter, InscriptionNewsletterAsso, Asso
from ateliers.models import Atelier
from .settings.production import SERVER_EMAIL, EMAIL_HOST_PASSWORD
from django.http import HttpResponseForbidden
from django.core.mail.message import EmailMultiAlternatives
import re
from django.core import mail
from actstream import actions
from bs4 import BeautifulSoup
from .forms import Adhesion_permacatForm, Adhesion_assoForm, creerAction_articlenouveauForm, AssocierProfil_adherentConf
from actstream import action
from actstream.models import followers
from datetime import datetime, timedelta
from django.utils.html import strip_tags
from .emails_templates import get_emailNexsletter2023
from hitcount.models import HitCount
from actstream.models import following
from django.db.models import Q
from bourseLibre.settings.production import LOCALL

def getMessage(action):
    message = action.data['message']
    if "a commenté" in message:
        mess = message.split("a commenté ")
        message = mess[1] + " a été commenté"
    return message


def getListeMailsAlerte():
    actions = Action.objects.filter(verb='emails')
    print('Nb actions : ' + str(len(actions)))
    messagesParMails = {}
    for action in actions:
        if 'emails' in action.data:
            for mail in action.data['emails']:
                message = getMessage(action)
                if not mail in messagesParMails:
                    messagesParMails[mail] = [message, ]
                else:
                    for x in messagesParMails[mail]:
                        if not message in messagesParMails[mail]:
                            messagesParMails[mail].append(message)

    listeMails = []
    for mail, messages in messagesParMails.items():
        titre = "[Perma.Cat] Du nouveau sur Perma.Cat"
        try:
            pseudo = Profil.objects.get(email=mail).username
        except:
            pseudo = ""
        messagetxt = "Bonjour / Bon dia, Voici les dernières nouvelles des pages auxquelles vous êtes abonné.e :\n"
        message = "<p>Bonjour / Bon dia,</p><p>Voici les dernières nouvelles des pages auxquelles vous êtes abonné.e :</p><ul>"
        liste_messages = []
        for m in messages:
            liste_messages.append("<li>" + m + "</li>")
            try:
                r = re.search("htt(.*?)>", m).group(1)[:-1]
                messagetxt += re.sub('<[^>]+>', '', m) + " : htt" + r + "\n"
            except:
                messagetxt += re.sub('<[^>]+>', '', m) + "\n"
        liste_messages.sort()
        message += "".join(liste_messages)

        messagetxt += "\nFins Aviat !\n---------------\nPour voir toute l'activité sur le site, consultez les Notifications : https://www.perma.cat/notifications/activite/ \n" + \
                      "Pour vous désinscrire des alertes mails, barrez les cloches sur le site (ou consultez la FAQ : https://www.perma.cat/faq/) "
        message += "</ul><br><p>Fins Aviat !</p><hr>" + \
                   "<p><small>Pour voir toute l'activité sur le site, consultez les <a href='https://www.perma.cat/notifications/activite/'>Notifications </a> </small>. " + \
                   "<small>Pour vous désinscrire des alertes mails, barrez les cloches sur le site (ou supprimez  <a href='https://www.perma.cat/accounts/mesSuivis/'>vos abonnements</a> ou consultez la <a href='https://www.perma.cat/faq/'>FAQ</a>)</small></p>"

        listeMails.append((titre, messagetxt, message, SERVER_EMAIL, [mail, ]))

    seen = set()
    listeMails_ok = []
    for x in listeMails:
        if x[1] not in seen:
            seen.add(x[1])
            listeMails_ok.append(x)
        else:
            i = next((i for i, mail in enumerate(listeMails_ok) if x[1] in mail), None)
            listeMails_ok[i][4].append(x[4][0])

    return listeMails_ok


def supprimerActionsEmails():
    actions = Action.objects.filter(verb='emails')
    for action in actions:
        action.delete()


def supprimerActionsStartedFollowing():
    actions = Action.objects.filter(verb='started following')
    for action in actions:
        action.delete()


def nettoyerActions(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    actions = Action.objects.all()
    for action in actions:
        if action is None or not hasattr(action,'_base_manager'):
            action.delete()
        else:
            if not action or not action.actor or not action.verb:
                action.delete()
    return redirect("bienvenue")


def abonnerAdherentsCiteAlt(request, ):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    profils = Profil.objects.filter(adherent_citealt=True)
    suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_citealt')

    for prof in profils:
        actions.follow(prof, suivi, actor_only=True, send_action=False)

    return redirect("bienvenue")


def nettoyerFollows(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    follows = Follow.objects.all()
    nombre = 0
    for action in follows:
        if action is None or not hasattr(action,'_base_manager'):
            action.delete()

        if not action.follow_object:
            action.delete()
            nombre += 1

    return render(request, 'admin/voirNettoyes.html', {'nombre': nombre, })

def nettoyerFollowsValide(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    nombre = 0
    follows = Follow.objects.all()
    for action in follows:
        if not action.follow_object:
            action.delete()
            nombre += 1

    return render(request, 'admin/voirNettoyes.html', {'nombre': 0, })

def nettoyerHistoriqueAdmin(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    from django.contrib.admin.models import LogEntry
    actions = LogEntry.objects.all()
    for action in actions:
        action.delete()

    return render(request, 'admin/voirActions.html', {'actions': actions, })


def get_articles_a_archiver():
    from blog.models import Article, Evenement
    from datetime import datetime, timedelta, date
    import pytz
    utc = pytz.UTC
    date_limite = utc.localize(datetime.today() - timedelta(days=90))
    articles = Article.objects.filter(estArchive=False, start_time__lte=date_limite)

    liste = []
    for article in articles:
        if article.start_time:
            liste.append(article)
    liste2 = []
    #from jardinpartage.models import Article as Article_jardin, Evenement as Evenement_jardin
    #articles = Article_jardin.objects.filter(estArchive=False, start_time__lte=date_limite)
    #for article in articles:
        #if article.start_time:
        #    liste2.append(article)

    liste4 = []
    ateliers = Atelier.objects.filter(estArchive=False, start_time__lte=date_limite)
    for a in ateliers:
        if a.start_time:
            liste4.append(a)

    liste3 = []
    for art in liste:
        eve = Evenement.objects.filter(start_time__lt=date_limite, end_time__lte=date_limite, article=art)
        if eve:
            liste3.append(art)

    for art in liste2:
        eve = Evenement_jardin.objects.filter(start_time__lt=date_limite, end_time__lte=date_limite, article=art)
        if eve:
            liste3.append(art)

    return liste, liste2, liste3, liste4


def voir_articles_a_archiver(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    listes = get_articles_a_archiver()
    return render(request, 'admin/voirArchivage.html', {'listes': listes})


def archiverArticles(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    listes = get_articles_a_archiver()
    for liste in listes:
        for art in liste:
            art.estArchive = True
            art.save(sendMail=False)

    return redirect('voir_articles_a_archiver', )


def voirEmails(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    listeMails = getListeMailsAlerte()
    return render(request, 'admin/voirEmails.html', {'listeMails': listeMails, })


def send_mass_html_mail(datatuple, fail_silently=False, auth_user=None,
                        auth_password=None, connection=None):
    """
    Given a datatuple of (subject, message, html_message, from_email,
    recipient_list), send each message to each recipient list.
    Return the number of emails sent.
    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user and auth_password are set, use them to log in.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.
    """
    # import re
    # EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    # decoupage en tranches de 90 receveurs max par mail
    data = []
    for subject, message, html_message, sender, recipient in datatuple:
        if len(recipient) > 90:
            for i in range(0, len(recipient), 90):
                data.append([subject, message, html_message, sender, recipient[i:i + 90]])
        else:
            data.append([subject, message, html_message, sender, recipient])

    connection = mail.get_connection(
        username=SERVER_EMAIL,
        password=EMAIL_HOST_PASSWORD,
        fail_silently=fail_silently,
    )
    messages= []
    for subject, message, html_message, sender, recipient in data :
        if recipient and recipient != [SERVER_EMAIL, ]:
            if len(recipient) == 1:
                messages.append(
                    EmailMultiAlternatives(subject, message, sender, to=recipient,
                                           alternatives=[(html_message, 'text/html')],
                                           connection=connection)
                )
            else:
                messages.append(
                    EmailMultiAlternatives(subject, message, sender, to=[SERVER_EMAIL, ],
                                           bcc=recipient,
                                           alternatives=[(html_message, 'text/html')],
                                           connection=connection)
                )
    #if LOCALL:
     #   return
    return connection.send_messages(messages)


def envoyerEmailsRequete(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    listeMails = getListeMailsAlerte()
    send_mass_html_mail(listeMails, fail_silently=False)

    supprimerActionsEmails()
    supprimerActionsStartedFollowing()
    return redirect('voirEmails', )


def envoyerEmailsTest(request):
    listeMails = []
    for i in range(2):
        listeMails.append(("titre", "messagetxt", "message_" + str(i), SERVER_EMAIL, [j for j in range(205)]))

    send_mass_html_mail(listeMails, fail_silently=False)


def envoyerEmails():
    print('Récupération des mails')
    listeMails = getListeMailsAlerte()

    print('Envoi des mails' + str(listeMails))
    send_mass_html_mail(listeMails, fail_silently=False)
    print('Suppression des alertes')
    supprimerActionsEmails()
    # supprimerActionsStartedFollowing()
    print('Fait')


def envoyerEmailstest():
    listeMails = []
    listeMails.append(('testCron', "message en txt", "<b>le message html</b>", SERVER_EMAIL, ["eloi.grau@gmail.com", ]))
    send_mass_html_mail(listeMails, fail_silently=False)


def decalerEvenements(request, num):
    return HttpResponseForbidden()
    #
    # from blog.models import Article, Projet, Evenement
    # from datetime import timedelta
    # decalage = timedelta(days=1)
    # if num == 0:
    #     for i, article in enumerate(Article.objects.all()):
    #             if article.start_time:
    #                 article.start_time = article.start_time + decalage
    #                 article.save()
    #                 print("ok1_"+str(i) + str(article))
    #             if article.end_time:
    #                 article.end_time = article.end_time + decalage
    #                 article.save()
    #                 print("ok2_"+str(i) + str(article))
    # if num == 1:
    #     for i, projet in enumerate(Projet.objects.all()):
    #             if projet.start_time:
    #                 projet.start_time = projet.start_time + decalage
    #                 projet.save()
    #                 print("ok1_"+str(i) + str(projet))
    #             if projet.end_time:
    #                 projet.end_time = projet.end_time + decalage
    #                 projet.save()
    #                 print("ok2_"+str(i) + str(projet))
    # if num == 2:
    #     for i, evenement in enumerate(Evenement.objects.all()):
    #             if evenement.start_time:
    #                 evenement.start_time = evenement.start_time + decalage
    #                 evenement.save()
    #                 print("ok1_"+str(i)+"_" + str(evenement))
    #             if evenement.end_time:
    #                 evenement.end_time = evenement.end_time + decalage
    #                 evenement.save()
    #                 print("ok2_" +str(i)+ str(evenement))
    #
    # if num == 3:
    #     from jardinpartage.models import Article as ArticleJP
    #     for i, evenement in enumerate(ArticleJP.objects.all()):
    #             if evenement.start_time:
    #                 evenement.start_time = evenement.start_time + decalage
    #                 evenement.save()
    #                 print("ok1_"+str(i)+"_" + str(evenement))
    #             if evenement.end_time:
    #                 evenement.end_time = evenement.end_time + decalage
    #                 evenement.save()
    #                 print("ok2_" +str(i)+ str(evenement))

    return redirect('bienvenue')


def voirPbProfils(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    adresses = Adresse.objects.all()
    pb_adresses = []
    for add in adresses:
        if add.getDistance(request.user.adresse) > 500:
            add.set_latlon_from_adresse()
            if add.getDistance(request.user.adresse) > 500:
                if add.code_postal == 66000:
                    add.commune = "Perpignan"
                    add.save()
                    add.set_latlon_from_adresse()
                    if add.getDistance(request.user.adresse) > 500:
                        pb_adresses.append(add)
    import requests
    profils = Profil.objects.all()
    pb_profils = []
    for profil in profils:
        if profil.description and not bool(BeautifulSoup(profil.description, "html.parser").find()):
            try:
                r = requests.post('https://validator.w3.org/nu/',
                                  data=profil.description, params={'out': 'json'},
                                  headers={
                                      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101    Safari/537.36',
                                      'Content-Type': 'text/html; charset=UTF-8'})

                pb_profils.append([profil, profil.description, r, ""])
            except:
                pb_profils.append([profil, profil.description, "none", "none"])

        if profil.competences and not bool(BeautifulSoup(profil.competences, "html.parser").find()):
            try:
                r = requests.post('https://validator.w3.org/nu/',
                                  data=profil.competences, params={'out': 'json'},
                                  headers={
                                      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101    Safari/537.36',
                                      'Content-Type': 'text/html; charset=UTF-8'})

                pb_profils.append([profil, profil.competences, r, ""])
            except:
                pb_profils.append([profil, profil.competences, "none", "none"])

    return render(request, 'admin/voirPbProfils.html', {'pb_profils': pb_profils, 'pb_adresses': pb_adresses})


def ajouterAdhesion(request, abreviationAsso):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if abreviationAsso == 'pc':
        form = Adhesion_permacatForm(request.POST or None)
    elif abreviationAsso == 'scic':
        form = Adhesion_assoForm(abreviationAsso, request.POST or None)

    if form.is_valid():
        form.save()
        return redirect(reverse('listeAdhesions', kwargs={"asso": abreviationAsso}))


    return render(request, 'asso/adhesion_ajouter.html', {"form": form, })

    #return render(request, 'erreur.html', {
    #    'msg': "Désolé, il n'est pas encore possible d'adhérer a une autre asso par ce biais, réservé permacat"})


def creerAction_articlenouveau(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = creerAction_articlenouveauForm(request.POST)
        if form.is_valid():
            article = form.cleaned_data["article"]
            suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_' + str(article.asso.abreviation))

            titre = "Nouvel article"
            message = "Un article a été posté dans le forum [" + str(
                article.asso.nom) + "] : '<a href='https://www.perma.cat" + article.get_absolute_url() + "'>" + article.titre + "</a>'"
            emails = [suiv.email for suiv in followers(suivi) if article.auteur != suiv and article.est_autorise(suiv)]
            if emails:
                action.send(article, verb='emails', url=article.get_absolute_url(), titre=titre, message=message,
                            emails=emails)
            return redirect("bienvenue")
    else:
        form = creerAction_articlenouveauForm()

    return render(request, 'admin/creerAction_articlenouveau.html', {"form": form, })


def getVieuxComptes(request, avertissement=False):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    if avertissement:
        date_limite = datetime(datetime.now().year - 1, datetime.now().month - 1, day=datetime.now().day)
    else:
        date_limite = datetime(datetime.now().year - 1, datetime.now().month, day=datetime.now().day)
    profil_jamais = Profil.objects.filter(Q(last_login__isnull=True) & ~Q(username='bot_permacat'))
    profil_old = Profil.objects.filter(Q(last_login__lt=date_limite) & ~Q(username='bot_permacat'))
    mail_jamais = {"titre": "[Perma.Cat] Suppression de votre compte",
            "contenu_html": "<p>Bonjour,</p> <br><p>il semble que vous ne vous êtes jamais connecté.e à <a href='https://www.perma.cat'>www.perma.cat</a>. Voulez-vous de l'aide pour y arriver ? N'hésitez pas à envoyer un mail à contact@perma.cat si besoin ou pour tout commentaire.</p> "+ \
                      " <p>Le site a beaucoup évolué depuis votre inscription, n'hésitez pas à venir y faire un tour. Si vous ne vous connectez pas d'ici 1 mois, nous supprimerons votre compte. Mais pas de panique, vous pourrez toujours vous réinscrire quand vous voudrez.</p> <br><p>Fins Aviat !</p>",
            "contenu": "Bonjour, il semble que vous ne vous êtes jamais connecté.e à www.perma.cat. Voulez-vous de l'aide pour y arriver ? N'hésitez pas à envoyer un mail à contact@perma.cat si besoin ou pour tout commentaire.  "+ \
                      " Si vous ne vous connectez pas d'ici 1 mois, nous supprimerons votre compte. Mais pas de panique, vous pourrez toujours vous réinscrire quand vous voudrez. Fins Aviat !",
            }
    mail_old = {"titre": "[Perma.Cat] Suppression de votre compte",
                "contenu_html": "<p>Bonjour,</p> <br><p>il semble que vous ne vous êtes pas connecté.e à <a href='https://www.perma.cat'>www.perma.cat</a> depuis plus d'un an. Voulez-vous de l'aide pour y arriver ? N'hésitez pas à envoyer un mail à contact@perma.cat si besoin ou pour tout commentaire.</p> " +\
                           "<p>Le site a beaucoup évolué depuis votre dernière venue, n'hésitez pas à venir y faire un tour. Si vous ne vous connectez pas d'ici 1 mois, nous supprimerons votre compte. Mais pas de panique, vous pourrez toujours vous réinscrire quand vous voudrez.</p><br> <p>Fins Aviat !</p>",
               "contenu": "Bonjour, il semble que vous ne vous êtes jamais connecté.e à www.perma.cat. Voulez-vous de l'aide pour y arriver ? N'hésitez pas à envoyer un mail à contact@perma.cat si besoin ou pour tout commentaire.  " + \
                          " Le site a beaucoup évolué depuis votre inscription, n'hésitez pas à venir y faire un tour. Si vous ne vous connectez pas d'ici 1 mois, nous supprimerons votre compte. Mais pas de panique, vous pourrez toujours vous réinscrire quand vous voudrez. Fins Aviat !",

    }
    return profil_jamais, profil_old, mail_jamais, mail_old

def supprimervieuxcomptes(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    profil_jamais, profil_old, mail, mail_old = getVieuxComptes(request, avertissement=False)
    # todo implementer suppression
    return render(request, 'admin/voirProfil_anciens.html',
                  {"mail2": mail_old, "mail": mail, 'profil_jamais': profil_jamais, 'profil_old': profil_old})

def envoyerMailVieuxComptes(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    profil_jamais, profil_old, mail_jamais, mail_old = getVieuxComptes(request, avertissement=True)
    listeMails = [] #subject, message, html_message, sender, recipient

    listeMails.append([mail_jamais['titre'], mail_jamais['contenu'], mail_jamais['contenu_html'], SERVER_EMAIL, [p.email for p in profil_jamais]])

    listeMails.append([mail_old['titre'], mail_old['contenu'], mail_old['contenu_html'], SERVER_EMAIL, [p.email for p in profil_old]])

    #send_mass_html_mail(listeMails, fail_silently=False)

    return render(request, 'admin/voirProfil_anciens.html',
                  {"listeMails": listeMails, 'profil_jamais': profil_jamais, 'profil_old': profil_old})


def getMailsNewsletter(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    # profils_1 = Profil.objects.filter(inscrit_newsletter=True)
    profils_2 = InscriptionNewsletter.objects.all()

    # return set([x.email for x in profils_1] + [x.email for x in profils_2])
    return set([x.email for x in profils_2])


def envoiNewsletter2023(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    titre, contenu_html = get_emailNexsletter2023()
    emails = getMailsNewsletter(request)
    contenu_txt = strip_tags(contenu_html)
    # emails = ("eloi.grau@gmail.com", )
    datatuple = [(titre, contenu_txt, contenu_html, SERVER_EMAIL, [email for email in emails])]
    # send_mass_html_mail(datatuple)
    return render(request, 'admin/voirMailsNewletter.html',
                  {"titre": titre, "contenu_txt": contenu_txt, "contenu_html": contenu_html, "emails": emails})


def supprimerHitsAnciens(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    date = datetime.now().date() - timedelta(days=int(366 * 1.2))
    hit_counts = HitCount.objects.filter(hit__created__lte=date)
    for hit in hit_counts:
        hit.delete()

    hit_counts2 = HitCount.objects.filter(hit__isnull=True)
    for hit in hit_counts2:
        hit.delete()

    return render(request, 'admin/supprimerHitsAnciens.html', {"hit_counts": hit_counts, })


def supprimerActionsAnciens(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    date = datetime.now().date() - timedelta(days=int(366 * 1.2))
    hit_counts = Action.objects.filter(timestamp__lte=date)
    for hit in hit_counts:
        hit.delete()
    return render(request, 'admin/supprimerHitsAnciens.html', {"hit_counts": hit_counts, })


def transforBlogJpToForum(request):
    from blog.models import Article as Article_blog
    from jardinpartage.models import Article as Article_jardin, Choix as Choix_jpt
    from .models import Asso
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    asso_jp = Asso.objects.get(abreviation="jp")

    for art in Article_jardin.objects.all():
        if not Article_blog.objects.filter(slug=art.slug).exists():
            new = Article_blog(
                categorie=art.categorie,
                titre="[" + Choix_jpt.getNomJardinFromNombre(art.jardin) + "] " + art.titre,
                auteur=art.auteur,
                slug=art.slug,
                contenu=art.contenu,
                date_creation=art.date_creation,
                date_modification=art.date_modification,
                estModifiable=art.estModifiable,
                asso=asso_jp,
                estArchive=art.estArchive,
                start_time=art.start_time,
                estEpingle=False
            ).save(sendMail=False)

    return redirect("blog:index_asso", asso='jp')


def movePermagoraInscritsToNewsletter(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    users = Profil.objects.filter(adherent_scic=True)
    asso = Asso.objects.get(abreviation="scic")

    #for u in users:
    #    InscriptionNewsletterAsso.objects.get_or_create(asso=asso, nom_newsletter="sympathisants", profil=u, email=u.email, )
    #    if not Adhesion_asso.objects.filter(user=u, asso=asso).exists():
    #        u.adherent_scic = False
    #        u.save()

    return redirect('listeContacts', "scic")


def reinitialiserAbonnementsPermAgora(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_scic')
    m = ""
    for p in Profil.objects.filter(adherent_scic=False):
        if suivi in following(p):
            actions.unfollow(p, suivi, send_action=False)
            m += "<p>"+p.username+" ne suit plus les articles permagora"+"</p>"

    for s in Suivis.objects.filter(nom_suivi__startswith='agora'):
        s.delete()
    return render(request, 'admin/admin_message.html', {"msg": m})


def inscrireProfilAuGroupe(request, id_profil, asso_abreviation):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    p = Profil.objects.get(id=id_profil)
    setattr(p, "adherent_" + asso_abreviation, True)
    p.save()
    suivi, created = Suivis.objects.get_or_create(nom_suivi="articles_" + asso_abreviation)
    actions.follow(p, suivi, send_action=False)
    return redirect(p.get_absolute_url())


def associerProfil_adherent(request, profil_pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    profil = Profil.objects.get(pk=profil_pk)
    form = AssocierProfil_adherentConf(request.POST or None)
    if form.is_valid():
        adherent = form.cleaned_data["adherent"]
        adherent.profil = profil
        adherent.save()
        return redirect(adherent)

    return render(request, 'adherents/associer_profil_adherent.html', {'form': form, "profil": profil})
