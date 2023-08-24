
from actstream import actions
from actstream.models import Follow, following
from .models import Choix, Suivis

def reabonnerProfil_base(profil):
    for suiv in Choix.suivisPossibles:
        suivi, created = Suivis.objects.get_or_create(nom_suivi=suiv)

        if not suivi in following(profil):
            actions.follow(profil, suivi, send_action=False)

    for abreviation in Choix.abreviationsAsso + ['public']:
        if profil.est_autorise(abreviation):
            suivi, created = Suivis.objects.get_or_create(nom_suivi="articles_" + abreviation)
            actions.follow(profil, suivi, send_action=False)
            #suivi, created = Suivis.objects.get_or_create(nom_suivi="agora_" + abreviation)
            #actions.follow(request.user, suivi, send_action=False)
