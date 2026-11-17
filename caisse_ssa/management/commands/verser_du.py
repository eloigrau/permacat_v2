from django.core.management.base import BaseCommand
from caisse_ssa.services import distribuer_dividende_universel


class Command(BaseCommand):
    help = "Calcule et verse automatiquement le Dividende Universel quotidien à tous les co-créateurs."

    def handle(self, *args, **options):
        journal, message = distribuer_dividende_universel()
        if journal:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.WARNING(message))