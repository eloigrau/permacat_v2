from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
# Create your models here.

class Notification(models.Model):
    # Les deux champs requis pour la GFK en base de données
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    # Le champ virtuel GFK
    target_object = GenericForeignKey('content_type', 'object_id')