from django.db import models
from django.urls import reverse
from bourseLibre.models import Profil
from bourseLibre.utils import slugify_pcat

import itertools
#from django.core.validators import RegexValidator

class Room(models.Model):
    """
    A room for people to chat in.
    """
    titre = models.CharField(max_length=255, )
    estPermanent = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
    date_creation = models.DateTimeField(auto_now_add=True, editable=False)
    updated_on = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        if not self.titre:
            self.titre = self.slug
            self.save()
        return self.titre + " *" if self.estPermanent else self.titre

    def save(self, *args, **kwargs):
        instance = super(Room, self).save()

        max_length = Room._meta.get_field('slug').max_length
        instance.slug = orig = slugify_pcat(instance.titre, max_length)

        for x in itertools.count(1):
            if not Room.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d"

        instance.save()

        return instance

    @property
    def group_name(self):
        """
        Returns the Channels Group name that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return "room-%s" % self.id

    def get_absolute_url(self):
        return reverse('permachat:room', kwargs={'room_name': self.slug})



class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(Profil, related_name='users', on_delete=models.CASCADE)
    content = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ('date_creation',)


    def __str__(self):
        return self.content