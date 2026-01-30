from django.urls import path

from . import views

app_name = 'permachat'

urlpatterns = [
    path("", views.index, name="index"),
    path("paint/<str:room_name>/", views.paint, name="paint"),
    path("room/<str:room_name>/", views.room, name="room"),
]