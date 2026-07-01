from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from blog.models import Cercle, Projet
from django.urls import reverse

class BudgetCercle(models.Model):
    titre = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    cercle = models.ForeignKey(Cercle, on_delete=models.CASCADE, null=True, related_name='budget_cercle')
    slug = models.SlugField(max_length=100)

    def __str__(self):
        return self.titre

    @property
    def get_absolute_url(self):
        return reverse('compta:tableau_de_bord',)

    def total_recettes(self):
        return sum(projet.total_recettes() for projet in self.budgetprojets.all())

    def total_depenses(self):
        return sum(projet.total_depenses() for projet in self.budgetprojets.all())

    def total_transfert(self):
        return sum(projet.total_transfert() for projet in self.budgetprojets.all())

    def solde(self):
        return self.total_recettes() - self.total_depenses()


class BudgetProjet(models.Model):
    budget_cercle = models.ForeignKey(BudgetCercle, on_delete=models.CASCADE, related_name='budgetprojets')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='projet_budget', null=False)
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    actif = models.BooleanField(default=True)
    slug = models.SlugField(max_length=100)

    def __str__(self):
        return f"{self.titre} (Projet : {self.projet.titre})"

    @property
    def get_titre(self):
        return self.titre

    @property
    def get_absolute_url(self):
        return reverse('compta:detail_projet', kwargs={'projet_id':self.id})

    def total_recettes(self):
        # Recettes classiques + Transferts reçus en tant que destination
        recettes_pures = self.transactions.filter(type_transaction='RECETTE').aggregate(
            total=models.Sum('montant'))['total'] or 0.0
        transferts_recus = Transaction.objects.filter(type_transaction='TRANSFERT', budget_destination=self).aggregate(
            total=models.Sum('montant'))['total'] or 0.0
        return float(recettes_pures) + float(transferts_recus)

    def total_transfert(self):
        # Dépenses classiques + Transferts émis (l'argent sort du projet)
        transferts_emis = self.transactions.filter(type_transaction='TRANSFERT').aggregate(
            total=models.Sum('montant'))['total'] or 0.0
        transferts_recus = Transaction.objects.filter(type_transaction='TRANSFERT', budget_destination=self).aggregate(
            total=models.Sum('montant'))['total'] or 0.0
        return float(transferts_recus) - float(transferts_emis)


    def total_depenses(self):
        # Dépenses classiques + Transferts émis (l'argent sort du projet)
        depenses_pures = self.transactions.filter(type_transaction='DEPENSE').aggregate(
            total=models.Sum('montant'))['total'] or 0.0
        transferts_emis = self.transactions.filter(type_transaction='TRANSFERT').aggregate(
            total=models.Sum('montant'))['total'] or 0.0
        return float(depenses_pures) + float(transferts_emis)

    def solde(self):
        return self.total_recettes() - self.total_depenses()


    #def ecart_previsionnel(self):
    #    """Différence entre le prévisionnel et les dépenses réelles totales."""
    #    return float(self.budget_previsionnel) - self.total_depenses()


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('RECETTE', 'Recette'),
        ('DEPENSE', 'Dépense'),
        ('TRANSFERT', 'Transfert sortant (vers un autre projet)'),
    ]

    # Le projet principal est le projet d'origine (celui qui paie ou encaisse)
    budget = models.ForeignKey(BudgetProjet, on_delete=models.CASCADE, related_name='transactions')

    # Champ requis uniquement en cas de TRANSFERT
    budget_destination = models.ForeignKey(
        BudgetProjet,
        on_delete=models.SET_NULL,
        related_name='transferts_recus',
        blank=True,
        null=True,
        help_text="Sélectionner uniquement s'il s'agit d'un transfert"
    )

    type_transaction = models.CharField(max_length=10, choices=TYPE_CHOICES)
    libelle = models.CharField(max_length=200, verbose_name="Libellé" )
    montant = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def clean(self):
        """Validation personnalisée de la cohérence des transferts."""
        super().clean()
        if self.type_transaction == 'TRANSFERT':
            if not self.budget_destination:
                raise ValidationError({'budget_destination': "Un projet de destination est obligatoire pour un transfert."})
            if self.projet == self.budget_destination:
                raise ValidationError({'budget_destination': "Le projet de destination doit être différent du projet d'origine."})
        elif self.budget_destination:
            # Si ce n'est pas un transfert mais qu'un projet a été sélectionné par erreur
            self.budget_destination = None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.type_transaction == 'TRANSFERT':
            return f"TRANSFERT: {self.projet.titre} → {self.budget_destination.titre} ({self.montant}€)"
        return f"{self.type_transaction} - {self.libelle} ({self.montant}€)"