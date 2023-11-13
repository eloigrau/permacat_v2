from bourseLibre.models import Suivis, Profil
from bourseLibre.constantes import Choix
from webpush import send_user_notification
from django.contrib.staticfiles.templatetags.staticfiles import static
from actstream import action


from django.dispatch import receiver
from django.core.signals import request_finished

#@receiver(request_finished)
#def post_detect_mention_callback(sender, **kwargs):
    # """ You will receive information of the mention
    # user_from: kwargs.get('user_from')
    #     User that mentions
    # object_pk: kwargs.get('object_pk')
    #     User's Pk that has been mentioned
    # target: kwargs.get('target')
    #     The object where the mention was made
    # """

# Your code here

def get_suivis_forum(request):
    return [("Public", 'public', Suivis.objects.get_or_create(nom_suivi="articles_public")[0]), ] + [
        (nom_asso, abreviation, Suivis.objects.get_or_create(nom_suivi="articles_" + abreviation)[0]) for
        abreviation, nom_asso in Choix.abreviationsNomsAsso if request.user.est_autorise(abreviation)]