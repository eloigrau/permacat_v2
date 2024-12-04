from django.urls import re_path
from django.contrib import admin
from . import views
admin.autodiscover()

app_name = 'phonebook'

urlpatterns = [
    re_path(r'^$', views.view_login, name='phonebook_login_page'),
    re_path(r'^logout/', views.view_logout, name='phonebook_logout'),
    re_path(r'^lists_contacts/', views.view_lists_contacts, name='phonebook_lists_contacts'),
    re_path(r'^search_contact/', views.view_search_contact, name='phonebook_search_contact'),
    re_path(r'^search_contact=(?P<query>\w+)', views.view_search_contact_query, name='phonebook_search_contact_query'),
    re_path(r'^new_contact/', views.view_new_contact, name='phonebook_new_contact'),
    re_path(r'^delete/(?P<contact_id>\d+)/$', views.view_delete, name='phonebook_delete'),
    re_path(r'^edit/(?P<contact_id>\d+)/$', views.view_edit_contact, name='phonebook_edit'),
    re_path(r'^call/(?P<num>\d+)/$', views.view_call, name='phonebook_call'),
    re_path(r'^exports_contacts/$', views.exports_contacts, name='phonebook_exports_contacts'),
]