from django.apps import AppConfig


class FichesConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'fiches'
    #
    # def ready(self):
    #     from actstream import registry
    #     registry.register(self.get_model('Article'))
    #     registry.register(self.get_model('Projet'))