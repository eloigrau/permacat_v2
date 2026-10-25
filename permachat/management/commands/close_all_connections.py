from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.management.base import BaseCommand
from django.core.cache import cache

ONLINE_CHANNELS_KEY = "global_permachat"

class Command(BaseCommand):
    help = 'Ferme de force toutes les connexions WebSocket actives du chat'

    def handle(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        connections = cache.get(ONLINE_CHANNELS_KEY, {})

        if not connections:
            self.stdout.write(self.style.WARNING("Aucune connexion active trouvée."))
            return

        count = 0
        # Parcourir chaque canal WebSocket actif
        for channel_name in list(connections.keys()):
            try:
                # Envoyer un ordre ASGI de fermeture directe au canal
                async_to_sync(channel_layer.send)(
                    channel_name,
                    {"type": "websocket.close"}
                )
                count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur pour le canal {channel_name}: {e}"))

        # Vider la liste des connectés dans Redis
        cache.delete(ONLINE_CHANNELS_KEY)

        self.stdout.write(self.style.SUCCESS(f"Succès : {count} connexions WebSocket ont été fermées de force."))