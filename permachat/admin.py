from django.contrib import admin
from .models import Room, Message


admin.site.register(
    Room,
    list_display=["id", "titre", "estPermanent"],
    list_display_links=["id", "titre"],
)

admin.site.register(
    Message,
    list_display=["id", "room", "user", 'content'],
    list_display_links=["id", "room"],
    search_fields = ('user__username', 'content', 'room')
)