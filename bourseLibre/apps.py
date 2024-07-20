from django.apps import AppConfig

class BourseLibreConfig(AppConfig):
    name = 'bourseLibre'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from actstream import registry
        from django.contrib.auth.models import Group
        from blog.models import Article, Projet, Commentaire, FicheProjet
        #from jardinpartage.models import Article as art_jardinpartage
        from ateliers.models import Atelier, InscriptionAtelier
        from fiches.models import Fiche, Atelier as fiche_at
        from vote.models import Suffrage
        from photologue.models import Document
        from photologue.models import Album
        from permagora.models import Commentaire_charte, PropositionCharte, Message_permagora
        from jardins.models import Jardin as Jardin_partage, Grainotheque
        from adherents.models import ListeDiffusionConf, Adherent
        registry.register(self.get_model('Profil'))
        registry.register(self.get_model('MessageGeneral'))
        registry.register(self.get_model('Message_salon'))
        registry.register(self.get_model('Produit'))
        registry.register(self.get_model('Conversation'))
        registry.register(self.get_model('Produit'))
        registry.register(self.get_model('Produit_vegetal'))
        registry.register(self.get_model('Produit_service'))
        registry.register(self.get_model('Produit_objet'))
        registry.register(self.get_model('Produit_aliment'))
        registry.register(self.get_model('Produit_offresEtDemandes'))
        registry.register(self.get_model('Suivis'))
        registry.register(self.get_model('Adhesion_permacat'))
        registry.register(self.get_model('Asso'))
        registry.register(self.get_model('Salon'))
        registry.register(self.get_model('InvitationDansSalon'))
        registry.register(self.get_model('Adresse'))
        registry.register(Document)
        registry.register(Atelier)
        registry.register(InscriptionAtelier)
        registry.register(Fiche)
        registry.register(fiche_at)
        registry.register(FicheProjet)
        registry.register(Article)
        registry.register(Commentaire)
        #registry.register(art_jardinpartage)
        registry.register(Projet)
        registry.register(Group)
        registry.register(Suffrage)
        registry.register(Album)
        registry.register(Commentaire_charte)
        registry.register(PropositionCharte)
        registry.register(Message_permagora)
        registry.register(Jardin_partage)
        registry.register(Grainotheque)
        registry.register(ListeDiffusionConf)
        registry.register(Adherent)


