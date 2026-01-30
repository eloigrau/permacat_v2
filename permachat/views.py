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
    room, created = Room.objects.get_or_create(slug=room_name)
    params = dict(request.GET.items())

    if created:
        if params["permanent"]:
            room.estPermanent = True
        room.name = room_name
        room.slug = slugify(room_name)
        room.save()
    messages = Message.objects.filter(room=room)[:30]
    print ('Roooommsg' + str(messages) + " " + str(params))
    return render(request, "permachat/room.html", {"room": room, "messages":messages})




@login_required
def paint(request, room_name):
    params = dict(request.GET.items())
    room, created = Room.objects.get_or_create(slug=room_name)
    if created:
        if params["permanent"]:
            room.estPermanent = True
        room.name = room_name
        room.slug = slugify(room_name)
        room.save()
    messages = Message.objects.filter(room=room)[:30]
    print ('Roooommsg' + str(messages) + " " + str(params) + str(room))
    return render(request, "permachat/paint.html", {"room": room, "messages":messages})