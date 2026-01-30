from django.db import models
from django.urls import reverse
from bourseLibre.models import Profil

class Room(models.Model):
    """
    A room for people to chat in.
    """
    titre = models.CharField(max_length=255)

    estPermanent = models.BooleanField(default=False)

    slug = models.SlugField(unique=True)

    def __str__(self):
        if not self.titre:
            self.titre = self.slug
            self.save()
        return self.titre + " (" + str(self.estPermanent) +")"


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
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)


    def __str__(self):
        return self.content