"""permagora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from permagora import views
from django.views.generic import TemplateView
#from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

# On import les vues de Django, avec un nom spécifique
from django.contrib.auth.decorators import login_required

# admin.autodiscover()
from django.contrib import admin

app_name = 'permagora'

urlpatterns = [
    path('gestion/', admin.site.urls),
    re_path(r'^summernote/', include('local_summernote.urls')),
    re_path(r'^captcha/', include('local_captcha.urls')),
    re_path(r'^$', views.bienvenue, name='bienvenue'),
    re_path(r'^planSite/$', views.planSite, name='planSite'),
    re_path(r'^risques/$', views.risques, name='risques'),
    re_path(r'^introduction/$', views.introduction, name='introduction'),
    re_path(r'^preambule/$', views.preambule, name='preambule'),
    re_path(r'^preconisations/$', views.preconisations, name='preconisations'),
    re_path(r'^faq/$', views.faq, name='faq'),
    re_path(r'^contact/$', views.contact, name='contact', ),
    re_path(r'^signer/$', views.signer, name='signer', ),
    re_path(r'^designer/$', views.designer, name='designer', ),
    re_path(r'^statistiques/$', views.statistiques, name='statistiques', ),
    re_path(r'^signataires/$', views.signataires, name='signataires', ),

    re_path(r'^accounts/profil/(?P<user_id>[0-9]+)/$', login_required(views.profil), name='profil', ),
    re_path(r'^accounts/profil/(?P<user_username>[-\w.]+)/$', login_required(views.profil_nom), name='profil_nom', ),
    re_path(r'^accounts/profile/$', login_required(views.profil_courant), name='profil_courant', ),

    re_path(r'^merci/$', views.merci, name='merci'),
    path('auth/', include('django.contrib.auth.urls')),
    re_path(r'^propositions/$', views.propositions, name='propositions', ),
    re_path(r'^organisationPermagora/$', views.organisationPermagora, name='organisationPermagora', ),
    re_path(r'^presentationPermagora/$', views.presentationPermagora, name='presentationPermagora', ),
    re_path(r'^cgu/$', views.cgu, name='cgu', ),
    re_path(r'^liens/$', views.liens, name='liens', ),
    re_path(r'^fairedon/$', views.fairedon, name='fairedon', ),
    re_path(r'^contact_admins/$', views.contact_admins, name='contact_admins',),

    re_path(r'^ajouterPoleCharte/$', views.ajouterPoleCharte, name='ajouterPoleCharte', ),
    re_path(r'^voirProposition/(?P<slug>[-\w]+)$', views.voirProposition, name='voirProposition', ),
    re_path(r'^ajouterVote_plus/(?P<slug>[-\w]+)$', views.ajouterVote_plus, name='ajouterVote_plus', ),
    re_path(r'^ajouterVote_moins/(?P<slug>[-\w]+)$', views.ajouterVote_moins, name='ajouterVote_moins', ),
    path(r'ajouterProposition/', views.ajouterProposition, name='ajouterProposition'),
    path(r'voirNotifications/', views.voirNotifications, name='voirNotifications'),

    re_path(r'^modifierProposition/(?P<slug>[-\w]+)$',
        login_required(views.ModifierProposition.as_view(), login_url='/auth/login/'), name='modifierProposition'),
    ]
urlpatterns += [
    re_path(r'^robots\.txt$', TemplateView.as_view(template_name="permagora/robots.txt", content_type='text/plain')),
]

from django.conf import settings
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'permagora.views.handler404'
handler500 = 'permagora.views.handler500'
handler400 = 'permagora.views.handler400'
handler403 = 'permagora.views.handler403'
