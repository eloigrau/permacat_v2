import uuid
from decimal import Decimal
from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError


DEVISE_CHOICES = [
    ('JUNE', 'June (Ğ1 - Monnaie Libre)'),
    ('EUROS', 'Euros (€)'),
]


class MembreSSA(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profil_ssa'
    )

    # 1. Gouvernance / Administration (Indépendant)
    est_membre_conseil = models.BooleanField(
        default=False,
        help_text="Membre du Conseil Collégial / Administrateur de la caisse"
    )
    # 2. Qualités économiques et monétaires (Modulables indépendamment)
    est_cotisant = models.BooleanField(
        default=True,
        help_text="Participe aux cotisations solidaires"
    )
    cotisation_mensuelle_engagee = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('0.00')
    )
    est_allocataire = models.BooleanField(
        default=True,
        help_text="Reçoit l'allocation alimentaire mensuelle de la caisse"
    )
    est_cocreateur_du = models.BooleanField(
        default=True,
        help_text="Co-crée quotidiennement le Dividende Universel (Monnaie Libre)"
    )

    def get_compte(self, devise):
        compte, _ = CompteMonnaieLocale.objects.get_or_create(
            proprietaire=self,
            devise=devise,
            defaults={'type_compte': 'ALLOCATAIRE'}
        )
        return compte

    def __str__(self):
        admin_badge = " [Conseil]" if self.est_membre_conseil else ""
        return f"{self.user.username}{admin_badge}"

class LieuDeVente(models.Model):
    TYPE_CHOICES = [
        ('PRODUCTEUR', 'Producteur direct / Ferme'),
        ('MARCHE', 'Stand de marché'),
        ('EPICERIE', 'Épicerie / Magasin'),
        ('GROUPEMENT', 'Groupement d’achat'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=150)
    type_lieu = models.CharField(max_length=20, choices=TYPE_CHOICES)
    gestionnaire = models.ForeignKey(
        MembreSSA, on_delete=models.PROTECT, related_name='lieux_geres'
    )
    adresse = models.TextField()
    siret = models.CharField(max_length=14, blank=True)
    code_paiement = models.CharField(max_length=12, unique=True, editable=False)
    est_conventionne = models.BooleanField(default=False)
    date_conventionnement = models.DateField(null=True, blank=True)

    def get_compte(self, devise):
        compte, _ = CompteMonnaieLocale.objects.get_or_create(
            lieu_de_vente=self,
            devise=devise,
            defaults={'type_compte': 'PROFESSIONNEL'}
        )
        return compte

    def save(self, *args, **kwargs):
        if not self.code_paiement:
            self.code_paiement = f"SSA-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} [{self.code_paiement}]"


class CompteMonnaieLocale(models.Model):
    """Portefeuille numérique séparé par devise (JUNE ou EUROS)."""
    TYPE_COMPTE = [
        ('CAISSE_CENTRALE', 'Compte Central de la Caisse'),
        ('ALLOCATAIRE', 'Compte Participant'),
        ('PROFESSIONNEL', 'Compte Producteur / Lieu conventionné'),
    ]
    proprietaire = models.ForeignKey(
        MembreSSA, on_delete=models.CASCADE, related_name='comptes', null=True, blank=True
    )
    lieu_de_vente = models.ForeignKey(
        LieuDeVente, on_delete=models.CASCADE, related_name='comptes', null=True, blank=True
    )
    type_compte = models.CharField(max_length=20, choices=TYPE_COMPTE)
    devise = models.CharField(max_length=10, choices=DEVISE_CHOICES, default='JUNE')
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['proprietaire', 'devise'],
                condition=models.Q(proprietaire__isnull=False),
                name='unique_compte_membre_devise'
            ),
            models.UniqueConstraint(
                fields=['lieu_de_vente', 'devise'],
                condition=models.Q(lieu_de_vente__isnull=False),
                name='unique_compte_lieu_devise'
            ),
        ]

    @classmethod
    def get_caisse_centrale(cls, devise):
        caisse, _ = cls.objects.get_or_create(
            type_compte='CAISSE_CENTRALE',
            devise=devise,
            proprietaire=None,
            lieu_de_vente=None
        )
        return caisse

    def __str__(self):
        nom = self.lieu_de_vente.nom if self.lieu_de_vente else (
            self.proprietaire.user.username if self.proprietaire else "Caisse Centrale"
        )
        return f"Compte {nom} [{self.devise}] : {self.solde}"


class Cotisation(models.Model):
    """Enregistrement d'une cotisation solidaire dans la caisse JUNE ou EUROS."""
    MOYEN_CHOICES = [
        ('JUNE_PORTEFEUILLE', 'Débit portefeuille June (Ğ1)'),
        ('VIREMENT_EUROS', 'Virement bancaire (€)'),
        ('ESPECES_EUROS', 'Espèces (€)'),
    ]
    membre = models.ForeignKey(MembreSSA, on_delete=models.PROTECT, related_name='cotisations')
    devise = models.CharField(max_length=10, choices=DEVISE_CHOICES, default='JUNE')
    montant = models.DecimalField(max_digits=8, decimal_places=2)
    moyen_paiement = models.CharField(max_length=20, choices=MOYEN_CHOICES)
    date_versement = models.DateTimeField(auto_now_add=True)
    mois_concerne = models.DateField(help_text="Premier jour du mois concerné")
    validee = models.BooleanField(default=True)

    def clean(self):
        if self.montant <= 0:
            raise ValidationError("Le montant de la cotisation doit être strictement positif.")

        # Vérification stricte : interdiction de cotiser si un solde est négatif
        compte_june = self.membre.get_compte('JUNE')
        compte_euros = self.membre.get_compte('EUROS')
        if compte_june.solde < 0 or compte_euros.solde < 0:
            raise ValidationError(
                "Cotisation refusée : le membre présente un solde négatif."
            )

        # Si cotisation en June, vérifie que le portefeuille June couvre la cotisation
        if self.devise == 'JUNE' and compte_june.solde < self.montant:
            raise ValidationError(
                f"Solde June insuffisant pour cotiser ({compte_june.solde} Ğ1 disponibles, {self.montant} Ğ1 requis)."
            )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        with transaction.atomic():
            if is_new:
                self.full_clean()
            super().save(*args, **kwargs)

            if is_new and self.validee:
                caisse_centrale = CompteMonnaieLocale.get_caisse_centrale(self.devise)
                if self.devise == 'JUNE':
                    # Virement interne traçable depuis le compte June du membre vers la Caisse June
                    compte_membre = self.membre.get_compte('JUNE')
                    Transaction.objects.create(
                        emetteur=compte_membre,
                        destinataire=caisse_centrale,
                        devise='JUNE',
                        montant=self.montant,
                        type_transaction='COTISATION',
                        libelle=f"Cotisation solidaire ({self.mois_concerne:%m/%Y})"
                    )
                else:
                    # Apport externe en Euros -> crédite la Caisse Centrale Euros
                    caisse_centrale.solde += self.montant
                    caisse_centrale.save()

    def __str__(self):
        return f"Cotisation {self.membre.user.username} - {self.montant} {self.devise}"


class Transaction(models.Model):
    TYPE_TRANSACTION = [
        ('CREATION_DU', 'Création monétaire - Dividende Universel (DU)'),
        ('COTISATION', 'Cotisation solidaire (Membre -> Caisse)'),
        ('ALLOCATION', 'Versement allocation mensuelle (Caisse -> Participant)'),
        ('PAIEMENT_ACHAT', 'Achat alimentaire (Participant -> Lieu conventionné)'),
        ('RECONVERSION', 'Remboursement en euros (Professionnel -> Caisse)'),
    ]
    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    devise = models.CharField(max_length=10, choices=DEVISE_CHOICES, default='JUNE')
    emetteur = models.ForeignKey(
        CompteMonnaieLocale, on_delete=models.PROTECT,
        related_name='transactions_emises', null=True, blank=True
    )
    destinataire = models.ForeignKey(
        CompteMonnaieLocale, on_delete=models.PROTECT, related_name='transactions_recues'
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    type_transaction = models.CharField(max_length=20, choices=TYPE_TRANSACTION)
    libelle = models.CharField(max_length=255, blank=True)
    date_execution = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.montant <= 0:
            raise ValidationError("Le montant doit être strictement positif.")
        if self.destinataire.devise != self.devise:
            raise ValidationError("Incohérence de devise sur le compte destinataire.")

        if self.type_transaction == 'CREATION_DU':
            if self.devise != 'JUNE':
                raise ValidationError("Le Dividende Universel ne peut être créé qu'en JUNE.")
            if self.emetteur is not None:
                raise ValidationError("Une création de DU ne doit pas avoir d'émetteur.")
        else:
            if not self.emetteur:
                raise ValidationError("Un compte émetteur est obligatoire.")
            if self.emetteur.devise != self.devise:
                raise ValidationError("Impossible de transférer entre deux devises différentes.")
            if self.emetteur == self.destinataire:
                raise ValidationError("L'émetteur et le destinataire doivent être différents.")
            if self.emetteur.solde < self.montant:
                raise ValidationError(f"Solde insuffisant ({self.emetteur.solde} {self.devise}).")

        if self.type_transaction == 'PAIEMENT_ACHAT':
            lieu = self.destinataire.lieu_de_vente
            if not lieu or not lieu.est_conventionne:
                raise ValidationError("Ce lieu n'est pas conventionné par la Caisse Alimentaire.")

    def save(self, *args, **kwargs):
        if not self.pk:
            with transaction.atomic():
                self.full_clean()
                if self.emetteur:
                    self.emetteur.solde -= self.montant
                    self.emetteur.save()
                self.destinataire.solde += self.montant
                self.destinataire.save()
                super().save(*args, **kwargs)
        else:
            raise ValidationError("Une transaction validée est immuable.")


class JournalDividendeUniversel(models.Model):
    date_du = models.DateField(unique=True)
    masse_monetaire_avant = models.DecimalField(max_digits=14, decimal_places=2)
    nombre_cocreateurs = models.PositiveIntegerField()
    montant_du_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    masse_creee_totale = models.DecimalField(max_digits=14, decimal_places=2)
    date_execution = models.DateTimeField(auto_now_add=True)