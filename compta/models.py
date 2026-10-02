from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from blog.models import Cercle, Projet
from bourseLibre.models import Asso
from django.urls import reverse
from decimal import Decimal
from django.db import models
from django.db import models, transaction
from django.utils import timezone
from bourseLibre.utils import slugify_pcat_mini

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
        return reverse('compta:detail_budget', kwargs={'budget_id':self.id})

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


    def get_absolute_url(self):
        return self.budget.get_absolute_url

    def get_update_url(self):
        return reverse('compta:modifier_transaction', kwargs={'pk':self.pk})

    def get_delete_url(self):
        return reverse('compta:supprimer_transaction', kwargs={'pk':self.pk})


class DocumentType(models.TextChoices):
    DEVIS = 'DEVIS', 'Devis'
    FACTURE = 'FACTURE', 'Facture'

class DocumentStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Brouillon'
    SENT = 'SENT', 'Envoyé'
    ACCEPTED = 'ACCEPTED', 'Accepté'
    REJECTED = 'REJECTED', 'Refusé'
    PAID = 'PAID', 'Payé'

# Sur ton modèle Facture (ou un modèle générique Document) :
class Client(models.Model):
    code_client = models.CharField(max_length=20, unique=True, verbose_name="Code Client", blank=True)
    name = models.CharField(max_length=255, verbose_name="Nom ou Raison sociale")
    address = models.TextField(verbose_name="Adresse")
    siret = models.CharField(max_length=20, blank=True, null=True, verbose_name="SIRET")
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    email = models.CharField(max_length=100, blank=True, null=True, verbose_name="Email")
    telephone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Telephone")
    infos = models.TextField(blank=True, null=True, verbose_name="Infos complémentaires")

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"[{self.code_client}] {self.name}"


    def save(self, asso, *args, **kwargs):
        if not self.code_client:
            self.asso = asso
            annee_en_cours = timezone.now().year
            prefixe = f"CLI-{slugify_pcat_mini(self.asso.nom[:5])}-{annee_en_cours}-"

            # Utilisation d'une transaction atomique pour éviter deux reçus avec le même numéro
            with transaction.atomic():
                derniere = Client.objects.select_for_update().filter(asso=self.asso,
                    code_client__startswith=prefixe
                ).order_by('id').last()

                if derniere:
                    # Extraction du dernier numéro séquentiel
                    dernier_numero = int(derniere.code_client.split('-')[-1])
                    nouveau_numero = dernier_numero + 1
                else:
                    nouveau_numero = 1

                # Formatage du numéro sur 5 chiffres (ex: 00001)
                self.code_client = f"{prefixe}{nouveau_numero:05d}"

        super().save(*args, **kwargs)

class Product(models.Model):
    code_product = models.CharField(max_length=20, unique=True, verbose_name="Code Produit", blank=True)
    name = models.CharField(max_length=255, verbose_name="Nom du produit")
    description = models.TextField(blank=True, verbose_name="Description")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix unitaire HT (€)"
    )
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return f"[{self.code_product}] {self.name} - {self.unit_price} €"

    def save(self, asso, *args, **kwargs):
        if not self.code_product:
            self.asso = asso
            annee_en_cours = timezone.now().year
            prefixe = f"P-{slugify_pcat_mini(self.asso.nom[:5])}-{annee_en_cours}-"

            # Utilisation d'une transaction atomique pour éviter deux reçus avec le même numéro
            with transaction.atomic():
                derniere = Product.objects.select_for_update().filter(asso=self.asso,
                    code_product__startswith=prefixe
                ).order_by('id').last()

                if derniere:
                    # Extraction du dernier numéro séquentiel
                    dernier_numero = int(derniere.code_product.split('-')[-1])
                    nouveau_numero = dernier_numero + 1
                else:
                    nouveau_numero = 1

                # Formatage du numéro sur 5 chiffres (ex: 00001)
                self.code_product = f"{prefixe}{nouveau_numero:05d}"

        super().save(*args, **kwargs)


class AssoInfo(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom / Raison sociale")
    #abreviation = models.CharField(max_length=3, verbose_name="Abreviation (3 lettres sans espaces)")
    siret = models.CharField(max_length=20, verbose_name="SIRET")
    iban = models.CharField(max_length=38, verbose_name="IBAN")
    bic = models.CharField(max_length=11, verbose_name="BIC")
    is_default = models.BooleanField(default=False, verbose_name="Vendeur par défaut")
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    adresse = models.TextField(max_length=255, null=True,)

    class Meta:
        verbose_name = "Vendeur"
        verbose_name_plural = "Vendeurs"
        constraints = [
            models.UniqueConstraint(fields=['asso', 'is_default'], name='unique defaut par Groupe')
        ]

    def __str__(self):
        return f"{self.name} ({self.siret})"

class Facture(models.Model):
    number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="factures", verbose_name="Client")
    created_at = models.DateField(auto_now_add=True, verbose_name="Date d'émission")
    date_echeance = models.DateField(verbose_name="Date d'échéance")

    # Informations du Vendeur (mémorisées par facture)
    # Association au modèle AssoInfo
    asso_info = models.ForeignKey(AssoInfo, on_delete=models.PROTECT, related_name="documents", verbose_name="AssoInfo", null=False, )
    project = models.CharField(max_length=255, blank=True, verbose_name="Projet / Marque commerciale")

    document_type = models.CharField(max_length=10, choices=DocumentType.choices, default=DocumentType.FACTURE)
    status = models.CharField(max_length=10, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    is_archived = models.BooleanField(default=False)
    facture_link = models.CharField(max_length=100, blank=True)

    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def __str__(self):
        return f"Facture {self.number} - {self.client.name}"

    def get_absolute_url(self):
        return reverse('compta:document_detail', kwargs={'pk':self.pk})

    @property
    def total_ht(self):
        return sum(item.total_ht for item in self.items.all())

    @property
    def total_ttc(self):
        # Franchise en base de TVA : HT == TTC
        return self.total_ht

    def save(self, asso_info=None, doc_type=None, *args, **kwargs):
        if not self.number and asso_info and doc_type:
            self.asso_info = asso_info
            self.asso = asso_info.asso
            self.document_type = doc_type
            pre_prefixe = "FA" if doc_type == DocumentType.FACTURE else "DEV"
            annee_en_cours = timezone.now().year
            prefixe = f"{pre_prefixe}-{slugify_pcat_mini(self.asso.nom[:5])}-{annee_en_cours}-"

            # Utilisation d'une transaction atomique pour éviter deux reçus avec le même numéro
            with transaction.atomic():
                derniere = Facture.objects.select_for_update().filter(asso=self.asso,
                    number__startswith=prefixe).order_by('id').last()

                if derniere:
                    # Extraction du dernier numéro séquentiel
                    dernier_numero = int(derniere.number.split('-')[-1])
                    nouveau_numero = dernier_numero + 1
                else:
                    nouveau_numero = 1

                # Formatage du numéro sur 5 chiffres (ex: 00001)
                self.number = f"{prefixe}{nouveau_numero:05d}"

        super().save(*args, **kwargs)

class FactureItem(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Produit")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Quantité")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix unitaire HT appliqué"
    )

    def __str__(self):
        return f"Facture {self.facture.number} - {self.product.name} - {self.quantity} - {self.total_ht} euros"

    class Meta:
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"

    def save(self, *args, **kwargs):
        # Utiliser automatiquement le prix actuel du produit si non spécifié
        if not self.unit_price:
            self.unit_price = float(self.product.unit_price)
        super().save(*args, **kwargs)

    @property
    def total_ht(self):
        return float(self.unit_price) * float(self.quantity)


class RecuFiscal(models.Model):
    TYPE_CHOICES = [
        ('DON', 'Don'),
        ('COTISATION', 'Cotisation'),
    ]

    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    asso_info = models.ForeignKey(AssoInfo, on_delete=models.CASCADE)
    nom_donateur = models.CharField(max_length=100)
    prenom_donateur = models.CharField(max_length=100)
    adresse_donateur = models.TextField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    type_versement = models.CharField(max_length=10, choices=TYPE_CHOICES, default='DON')
    numero_recu = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, verbose_name="Description")

    def __str__(self):
        return f"Reçu n°{self.numero_recu} - {self.nom_donateur}"

    def get_absolute_url(self):
        return reverse('compta:recu_detail', kwargs={'pk':self.pk})

    def save(self, asso, *args, **kwargs):
        if not self.numero_recu:
            self.asso = asso
            annee_en_cours = timezone.now().year
            prefixe = f"RF-{slugify_pcat_mini(self.asso.nom[:5])}-{annee_en_cours}-"

            # Utilisation d'une transaction atomique pour éviter deux reçus avec le même numéro
            with transaction.atomic():
                dernier_recu = RecuFiscal.objects.select_for_update().filter(asso=self.asso,
                    numero_recu__startswith=prefixe
                ).order_by('id').last()

                if dernier_recu:
                    # Extraction du dernier numéro séquentiel
                    dernier_numero = int(dernier_recu.numero_recu.split('-')[-1])
                    nouveau_numero = dernier_numero + 1
                else:
                    nouveau_numero = 1

                # Formatage du numéro sur 5 chiffres (ex: 00001)
                self.numero_recu = f"{prefixe}{nouveau_numero:05d}"

        super().save(*args, **kwargs)