from django.urls import path

from . import views

app_name = 'permapaint'

urlpatterns = [
    path("", views.paint, name="index"),
    # path("files/", views.files, name="files"),
    # path("download/", views.download_image, name="download"),
    # path("search/", views.search, name="search"),
]