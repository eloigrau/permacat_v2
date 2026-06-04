from django.contrib import admin
from .models import Room, Message
from django.contrib.admin import site, ModelAdmin, TabularInline

# admin.site.register(
#     Room,
#     list_display=["id", "titre", "estPermanent"],
#     list_display_links=["id", "titre"],
# )
#
# admin.site.register(
#     Message,
#     list_display=["id", "room", "user", 'content'],
#     list_display_links=["id", "room"],
#     search_fields = ('user__username', 'content', 'room')
# )



class RoomAdmin(ModelAdmin):
    """
    Just a name display and its date(s).
    """

    class InlineMessageAdmin(TabularInline):
        """
        Shows the last messages in the room.
        """

        model = Message

        def has_add_permission(self, request, obj):
            return False

        def has_change_permission(self, request, obj=None):
            return obj is None

        def has_delete_permission(self, request, obj=None):
            return False

        max_num = 50
        extra = 0
        ordering = ["date_creation"]

    list_display = ["date_creation", "updated_on", "titre"]
    ordering = ["titre"]
    inlines = [InlineMessageAdmin]


class MessageAdmin(ModelAdmin):
    """
    Allows a lookup of a message by its content.
    """

    list_display = ["date_creation", "user", "room", "content"]
    list_display_links = ["date_creation"]
    search_fields = ["content"]
    ordering = ["date_creation"]

    #def has_add_permission(self, request):
    #    return False

    #def has_change_permission(self, request, obj=None):
    #    return obj is None


# Register your models here.
site.register(Room, RoomAdmin)
site.register(Message, MessageAdmin)