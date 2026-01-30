# chat/routing.py
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    #path(r"ws/chat/<str:room_name>/", consumers.ChatConsumer.as_asgi()),
    #path(r"permachat/stream/", consumers.ChatConsumer),
    path("permachat/stream/", consumers.ChatConsumer.as_asgi()),
    path("permachat/paint/<str:roomName>", consumers.ChatConsumer.as_asgi()),
]