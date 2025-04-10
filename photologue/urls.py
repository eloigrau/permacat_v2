
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from . import views


"""NOTE: the url names are changing. In the long term, I want to remove the ''
prefix on all urls, and instead rely on an application namespace 'photologue'.

At the same time, I want to change some URL patterns, e.g. for pagination. Changing the urls
twice within a few releases, could be confusing, so instead I am updating URLs bit by bit.

The new style will coexist with the existing '' prefix for a couple of releases.

"""


app_name = 'photologue'

urlpatterns = [
    re_path(r'^album/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$', login_required(views.AlbumDateDetailView.as_view(month_format='%m')), name='album-detail'),
    re_path(r'^album/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/$', login_required(views.AlbumDayArchiveView.as_view(month_format='%m')), name='album-archive-day'),
    re_path(r'^album/(?P<year>\d{4})/(?P<month>[0-9]{2})/$', login_required(views.AlbumMonthArchiveView.as_view(month_format='%m')), name='album-archive-month'),
    re_path(r'^album/(?P<year>\d{4})/$', login_required(views.AlbumYearArchiveView.as_view()), name='album-archive-year'),
    re_path(r'^album/$', login_required(views.AlbumArchiveIndexView.as_view()), name='album-archive'),
    re_path(r'^$', RedirectView.as_view( url=reverse_lazy('photologue:album-archive'), permanent=True), name='photologue-root'),
    re_path(r'^album/(?P<slug>[\-\d\w]+)/$', login_required(views.AlbumDetailView.as_view()), name='album'),
    re_path(r'^albumlist/$', login_required(views.AlbumListView.as_view()), name='album-list'),
    re_path(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$', login_required(views.PhotoDateDetailView.as_view(month_format='%m')),
        name='photo-detail'),
    re_path(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/$', login_required(views.PhotoDayArchiveView.as_view(month_format='%m')), name='photo-archive-day'),
    re_path(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/$', login_required(views.PhotoMonthArchiveView.as_view(month_format='%m')), name='photo-archive-month'),
    re_path(r'^photo/(?P<year>\d{4})/$', login_required(views.PhotoYearArchiveView.as_view()), name='photo-archive-year'),
    re_path(r'^photo/$', login_required(views.PhotoArchiveIndexView.as_view()), name='photo-archive'),

    re_path(r'^photo/(?P<slug>[\-\d\w]+)/$', login_required(views.PhotoDetailView.as_view()), name='photo'),
    re_path(r'^photolist/$', login_required(views.PhotoListView.as_view()), name='photo-list'),
    re_path(r'^doclist/$', login_required(views.DocListView.as_view()), name='doc-list'),
    re_path(r'^filtrer_documents/$', views.filtrer_documents, name='filtrer_documents'),
    re_path(r'^ajouterPhoto/(?P<albumSlug>[\-\d\w]+)$', views.ajouterPhoto, name='ajouterPhoto'),
    re_path(r'^ajouterAlbum/$', views.ajouterAlbum, name='ajouterAlbum'),
    path(r'ajouterDocument/<str:article_slug>', views.ajouterDocument, name='ajouterDocument'),
    path(r'associerDocumentArticle/<str:doc_slug>', views.associerDocumentArticle, name='associerDocumentArticle'),

    re_path(r'^modifierAlbum/(?P<slug>[\-\d\w]+)$', login_required(views.ModifierAlbum.as_view(), login_url='/auth/login/'), name='modifierAlbum'),
    re_path(r'^supprimerAlbum/(?P<slug>[\-\d\w]+)$', login_required(views.SupprimerAlbum.as_view(), login_url='/auth/login/'), name='supprimerAlbum'),
    re_path(r'^modifierPhoto/(?P<slug>[\-\d\w]+)$', login_required(views.ModifierPhoto.as_view(), login_url='/auth/login/'), name='modifierPhoto'),
    re_path(r'^supprimerPhoto/(?P<slug>[\-\d\w]+)$', login_required(views.SupprimerPhoto.as_view(), login_url='/auth/login/'), name='supprimerPhoto'),

    re_path(r'^supprimerDocument/(?P<slug>[\-\d\w]+)$',
        login_required(views.SupprimerDocument.as_view(), login_url='/auth/login/'), name='supprimerDocument'),
    re_path(r'^modifierDocument/(?P<slug>[\-\d\w]+)$',
        login_required(views.ModifierDocument.as_view(), login_url='/auth/login/'), name='modifierDocument'),

    re_path(r'^telechargerDocument/(?P<slug>[\-\d\w]+)$',login_required(views.telechargerDocument), name='telechargerDocument'),

    re_path(r'^suivre_albums/$', views.suivre_albums, name='suivre_albums'),
    re_path(r'^suivre_documents/$', views.suivre_documents, name='suivre_documents'),

]
