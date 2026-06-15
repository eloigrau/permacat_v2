from django.core.management.base import BaseCommand
from django.utils.text import slugify
from compta.models import BudgetCercle, BudgetProjet
from blog.models import Projet

DATA = [
    ("Ancrage", "#4FA8C7", "🎓", [
    ]),
    ("Éducation", "#4FA8C7", "🎓", [
    ]),
    ("Jardin", "#5CB85C", "🌱", [
    ]),
    ("Labo d'idées", "#F0AD4E", "💡", [
    ]),
    ("Évènement", "#C0392B", "🎪", [
    ]),
]
class Command(BaseCommand):
    help = "Pré-remplit les 4 cercles et leurs sous-activités"

    def handle(self, *args, **opts):
        from bourseLibre.models import Asso
        from blog.models import Cercle, Projet
        asso = Asso.objects.get(slug="scic")

        for i, (titre, couleur, icone, subs) in enumerate(DATA):
            cercle, created = Cercle.objects.get_or_create(titre=titre, slug=slugify(titre), asso=asso)
            budget_cercle, created = BudgetCercle.objects.get_or_create(
                titre=titre,
                slug=slugify(titre),
                cercle=cercle,
            )
            self.stdout.write(self.style.SUCCESS(f"✓ création cercle : {titre} "))

        cercle_a = Cercle.objects.get(asso=asso, slug="ancrage")

        for p in Projet.objects.filter(asso=asso):
            p.cercle = cercle_a
            p.save()
            budget_projet, created = BudgetProjet.objects.get_or_create(projet=p, budget_cercle=cercle_a.budget_cercle, titre="Budget général")
            self.stdout.write(self.style.SUCCESS(f"✓ création budget : {budget_projet} "))