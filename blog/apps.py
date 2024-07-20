from django.apps import AppConfig
#from exo_mentions.registry import register
#from .models import Commentaire
#from .utils import post_detect_mention_callback

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'blog'
    #
    # def ready(self):
    #     from actstream import registry
    #     registry.register(self.get_model('Article'))
    #     registry.register(self.get_model('Projet'))

    # def ready(self):
    #     model = Commentaire
    #     field = 'commentaire'
    #     callback = post_detect_mention_callback
    #
    #     register(model, field, callback)