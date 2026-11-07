from actstream import actions
from actstream.models import Follow, following
from .models import Choix, Suivis, Asso, Salon
import uuid
from django.utils.text import slugify
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin

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

def slugify_pcat(titre, max_length=50):
    slug = slugify(titre)[:max_length]
    if slug == '':
        slug = uuid.uuid4()
    return slug

def slugify_pcat_mini(titre):
    return slugify_pcat(titre, 3).replace('-','').upper()

def testIsMembreSalon(request, slug):
    salon = get_object_or_404(Salon, slug=slug)
    if not salon.est_autorise(request.user) and not request.user.is_superuser:
        return render(request, 'notMembre.html', {'asso':salon.titre } )
    return salon


def testIsMembreAsso_bool(request, asso):
    if asso == "public":
        return Asso.objects.get(nom="Public")

    assos = Asso.objects.filter(Q(nom=asso) | Q(slug=asso))
    if assos:
        assos = assos[0]

        if not assos.is_membre(request.user) and not request.user.is_superuser:
            return None
        return assos

    return Asso.objects.get(nom="Public")

def testIsMembreAsso(request, asso):
    if asso == "public":
        return Asso.objects.get(nom="Public")

    assos = Asso.objects.filter(Q(nom=asso) | Q(slug=asso))
    if assos:
        assos = assos[0]

        if not assos.is_membre(request.user) and not request.user.is_superuser:
            return render(request, 'notMembre.html', {'asso':assos } )

        request.session["asso_slug"] = assos.slug
        return assos

    return Asso.objects.get(nom="Public")


class TestMembreAssoMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        try:
            if "asso_slug" in self.request.GET:
                self.asso = Asso.objects.get(slug=self.request.GET["asso_slug"])
                self.request.session["asso_slug"] = self.asso.slug
            elif "asso_slug" in self.request.session:
                self.asso = Asso.objects.get(slug=self.request.session["asso_slug"])
            return self.asso.est_autorise(self.request.user) or self.request.user.is_superuser
        except:
            return False

class TestBureauAssoMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            self.asso = Asso.objects.get(slug=self.kwargs["asso_slug"])
            self.request.session["asso_slug"] = self.asso.slug
            return self.request.user.estmembre_bureau(self.asso.slug) or self.request.user.is_superuser
        except:
            return False


import logging
import socket

from django.core.cache import cache
DEFAULT_TIMEOUT = cache.default_timeout

logger = logging.getLogger(__name__)

def safe_cache_delete(key):
    """Safely deletes a given key from the cache."""
    _ = safe_cache_get(key) and cache.delete(key)


def safe_cache_set(key, value, timeout=DEFAULT_TIMEOUT):
    """
    Safely set a value in the cache.

    If the cache is not reachable, the operation silently fails.

    :param key: The cache key to set.
    :param value: The value to store in the cache.
    :param timeout: The cache timeout in seconds. If None,
        the default cache timeout will be used.
    """
    try:
        cache.set(key, value, timeout)
    except ConnectionError as exc:
        # Handle cache connection error
        logger.exception(exc)
    except socket.error as exc:
        # Handle other potential connection errors, especially for
        # older Python versions
        logger.exception(exc)


def safe_cache_get(key, default=None):
    """
    Safely get a value from the cache.

    If the cache is not reachable, the operation silently fails.

    :param key: The cache key to get.
    :param default: The default value to return if the key is not found.
    :return: The value from the cache or the default value.
    """
    try:
        return cache.get(key, default)
    except ConnectionError as exc:
        # Handle cache connection error
        logger.exception(exc)
        return default
    except socket.error as exc:
        # Handle other potential connection errors, especially for
        # older Python versions
        logger.exception(exc)
        return default