from django.db import models
from blog.models import Projet
from bourseLibre.models import Asso

class ProjetBoard(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='board', blank=True, null=True)
    asso = models.ForeignKey(Asso, on_delete=models.CASCADE, blank=False, null=False)
    #membres = models.ManyToManyField(Profil, related_name='projets', blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class Colonne(models.Model):
    projet = models.ForeignKey(ProjetBoard, on_delete=models.CASCADE, related_name='colonnes')
    titre = models.CharField(max_length=100) # Ex: "À faire", "En cours", "Fait"
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f"{self.projet.nom} - {self.titre}"

class Tache(models.Model):
    colonne = models.ForeignKey(Colonne, on_delete=models.CASCADE, related_name='taches')
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    #assignes = models.ManyToManyField(Profil, related_name='taches_assignees', blank=True)
    date_limite = models.DateField(null=True, blank=True)
    ordre = models.PositiveIntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordre', '-date_creation']

    def __str__(self):
        return self.titre