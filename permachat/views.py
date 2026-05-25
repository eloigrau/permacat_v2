from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Room, Message
from django.utils.text import slugify



@login_required
def index(request):
    """
    Root page view. This is essentially a single-page app, if you ignore the
    login and admin parts.
    """
    # Get a list of rooms, ordered alphabetically
    rooms = Room.objects.order_by("titre")

    # Render that in the index template
    return render(request, "permachat/index.html", {
        "rooms": rooms,
    })


@login_required
def room(request, room_name):
    messages = []
    room, created = Room.objects.get_or_create(slug=room_name) #get_room_or_error(room_name, request.user)
    params = dict(request.GET.items())

    if created:
        if "permanent" in params and params["permanent"]:
            room.estPermanent = True
        room.titre = room_name
        room.slug = slugify(room_name)
        room.save()

    if room.estPermanent:
        messages = Message.objects.filter(room=room)[:30]

    return render(request, "permachat/room.html", {"room": room, "messages":messages})

@login_required
def room_new(request):
    return render(request, "permachat/room_new.html", {})




@login_required
def paint(request, room_name):
    params = dict(request.GET.items())
    room, created = Room.objects.get_or_create(slug=room_name)
    if created:
        if "permanent" in params and params["permanent"]:
            room.estPermanent = True
        else:
            room.estPermanent = False
        room.titre = room_name
        room.slug = slugify(room_name)
        room.save()
    messages = Message.objects.filter(room=room)[:30]
    return render(request, "permachat/paint.html", {"room": room, "messages":messages})