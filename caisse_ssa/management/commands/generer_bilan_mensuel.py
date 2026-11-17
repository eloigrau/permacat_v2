from django.core.management.base import BaseCommand
from django.utils import timezone
from caisse_ssa.pdf_reports import generer_pdf_bilan_mensuel


class Command(BaseCommand):
    help = "Génère et archive le bilan PDF mensuel des caisses et transactions."

    def add_arguments(self, parser):
        parser.add_argument('--annee', type=int, help="Année du bilan (ex: 2026)")
        parser.add_argument('--mois', type=int, help="Mois du bilan (1 à 12)")

    def handle(self, *args, **options):
        now = timezone.localdate()
        annee = options['annee']
        mois = options['mois']

        # Par défaut : génère le bilan du mois précédent
        if not annee or not mois:
            if now.month == 1:
                annee, mois = now.year - 1, 12
            else:
                annee, mois = now.year, now.month - 1

        generer_pdf_bilan_mensuel(annee, mois, sauvegarder_fichier=True)
        self.stdout.write(
            self.style.SUCCESS(f"Bilan PDF généré et archivé pour {mois:02d}/{annee}.")
        )