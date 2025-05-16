from actstream import actions
from actstream.models import Follow, following
from .models import Choix, Suivis
import uuid
from django.utils.text import slugify

def reabonnerProfil_base(profil):
    for suiv in Choix.suivisPossibles:
        suivi, created = Suivis.objects.get_or_create(nom_suivi=suiv)

        if not suivi in following(profil):
            actions.follow(profil, suivi, send_action=False)

    for slug in Choix.slugsAsso + ['public']:
        if profil.est_autorise(slug):
            suivi, created = Suivis.objects.get_or_create(nom_suivi="articles_" + slug)
            actions.follow(profil, suivi, send_action=False)
            #suivi, created = Suivis.objects.get_or_create(nom_suivi="agora_" + slug)
            #actions.follow(request.user, suivi, send_action=False)

def desabonnerProfil_base(profil):
    for suiv in Choix.suivisPossibles:
        suivi, created = Suivis.objects.get_or_create(nom_suivi=suiv)

        if suivi in following(profil):
            actions.unfollow(profil, suivi, send_action=False)

    for slug in Choix.slugsAsso + ['public']:
        if profil.est_autorise(slug):
            suivi, created = Suivis.objects.get_or_create(nom_suivi="articles_" + slug)
            actions.unfollow(profil, suivi, send_action=False)
            suivi, created = Suivis.objects.get_or_create(nom_suivi="agora_" + slug)
            actions.unfollow(profil, suivi, send_action=False)


def desabonnerProfil_particuliers(profil,):
    follows = Follow.objects.filter(user=profil)
    for action in follows:
        if not action.follow_object:
            action.delete()
        elif 'articles' in str(action.follow_object) and not str(action.follow_object) == "articles_jardin":
            pass
        elif 'agora' in str(action.follow_object):
            pass
        elif str(action.follow_object) in Choix.suivisPossibles:
            pass
        else:
            action.delete()

def desabonnerProfil_salons(profil):
    for salon in profil.get_salons():
        actions.unfollow(profil, salon.getSuivi(), send_action=False)

def reabonnerProfil_salons(profil):
    for salon in profil.get_salons():
        actions.follow(profil, salon.getSuivi(), send_action=False)

def slugify_pcat(titre, max_length):
    slug = slugify(titre)[:max_length]
    if slug == '':
        slug = uuid.uuid4()
    return slug
