from django.apps import AppConfig


class AteliersConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'ateliers'
    #
    # def ready(self):
    #     from actstream import registry
    #     registry.register(self.get_model('Article'))
    #     registry.register(self.get_model('Projet'))