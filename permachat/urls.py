from django.urls import path

from . import views

app_name = 'permachat'

urlpatterns = [
    path("", views.index, name="index"),
    path("image/<str:room_name>/", views.paint, name="paint"),
    path("room/<str:room_name>/", views.room, name="room"),
    path("chat/<str:room_name>/", views.room_new, name="room_new"),
]