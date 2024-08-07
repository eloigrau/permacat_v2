from django import forms
from django.conf import settings
from django.urls import path, include, re_path
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ngettext, gettext_lazy as _

from .forms import UploadZipForm
from .models import Album, Photo, PhotoEffect, PhotoSize, Document, Watermark

MULTISITE = getattr(settings, 'PHOTOLOGUE_MULTISITE', False)


class AlbumAdminForm(forms.ModelForm):
    class Meta:
        model = Album
        if MULTISITE:
            exclude = []
        else:
            exclude = ['sites']


class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'asso', 'date_creation', 'photo_count')
    list_filter = ['date_creation', 'asso']
    if MULTISITE:
        list_filter.append('sites')
    date_hierarchy = 'date_creation'
    prepopulated_fields = {'slug': ('title',)}
    form = AlbumAdminForm
    if MULTISITE:
        filter_horizontal = ['sites']
    if MULTISITE:
        actions = [
            'add_to_current_site',
            'add_photos_to_current_site',
            'remove_from_current_site',
            'remove_photos_from_current_site'
        ]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """ Set the current site as initial value. """
        if db_field.name == "sites":
            kwargs["initial"] = [Site.objects.get_current()]
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_related(self, request, form, *args, **kwargs):
        """
        If the user has saved a album with a photo that belongs only to
        different Sites - it might cause much confusion. So let them know.
        """
        super().save_related(request, form, *args, **kwargs)
        #orphaned_photos = form.instance.orphaned_photos()
        #if orphaned_photos:
        #    msg = ngettext(
        #        'The following photo does not belong to the same site(s)'
        #        ' as the album, so will never be displayed: %(photo_list)s.',
         #       'The following photos do not belong to the same site(s)'
         #       ' as the album, so will never be displayed: %(photo_list)s.',
         #       len(orphaned_photos)
        #    ) % {'photo_list': ", ".join([photo.title for photo in orphaned_photos])}
         #   messages.warning(request, msg)

    def add_to_current_site(modeladmin, request, queryset):
        current_site = Site.objects.get_current()
        current_site.album_set.add(*queryset)
        msg = ngettext(
            "The album has been successfully added to %(site)s",
            "The galleries have been successfully added to %(site)s",
            len(queryset)
        ) % {'site': current_site.name}
        messages.success(request, msg)

    add_to_current_site.short_description = \
        _("Add selected galleries to the current site")

    def remove_from_current_site(modeladmin, request, queryset):
        current_site = Site.objects.get_current()
        current_site.album_set.remove(*queryset)
        msg = ngettext(
            "The album has been successfully removed from %(site)s",
            "The selected galleries have been successfully removed from %(site)s",
            len(queryset)
        ) % {'site': current_site.name}
        messages.success(request, msg)

    remove_from_current_site.short_description = \
        _("Remove selected galleries from the current site")

    def add_photos_to_current_site(modeladmin, request, queryset):
        photos = Photo.objects.filter(galleries__in=queryset)
        current_site = Site.objects.get_current()
        current_site.photo_set.add(*photos)
        msg = ngettext(
            'All photos in album %(galleries)s have been successfully added to %(site)s',
            'All photos in galleries %(galleries)s have been successfully added to %(site)s',
            len(queryset)
        ) % {'site': current_site.name,
             'galleries': ", ".join(["'{}'".format(album.title) for album in queryset])}
        messages.success(request, msg)

    add_photos_to_current_site.short_description = \
        _("Add all photos of selected galleries to the current site")

    def remove_photos_from_current_site(modeladmin, request, queryset):
        photos = Photo.objects.filter(galleries__in=queryset)
        current_site = Site.objects.get_current()
        current_site.photo_set.remove(*photos)
        msg = ngettext(
            'All photos in album %(galleries)s have been successfully removed from %(site)s',
            'All photos in galleries %(galleries)s have been successfully removed from %(site)s',
            len(queryset)
        ) % {'site': current_site.name,
             'galleries': ", ".join(["'{}'".format(album.title) for album in queryset])}
        messages.success(request, msg)

    remove_photos_from_current_site.short_description = \
        _("Remove all photos in selected galleries from the current site")


admin.site.register(Album, AlbumAdmin)


class PhotoAdminForm(forms.ModelForm):
    class Meta:
        model = Photo
        if MULTISITE:
            exclude = []
        else:
            exclude = ['sites']


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_creation',  'image')
    list_filter = ['date_creation',]
    if MULTISITE:
        list_filter.append('sites')
    search_fields = ['title', 'slug', 'caption']
    list_per_page = 10
    prepopulated_fields = {'slug': ('title',)}
    #readonly_fields = ('image.date_taken',)
    form = PhotoAdminForm
    if MULTISITE:
        filter_horizontal = ['sites']
    if MULTISITE:
        actions = ['add_photos_to_current_site', 'remove_photos_from_current_site']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """ Set the current site as initial value. """
        if db_field.name == "sites":
            kwargs["initial"] = [Site.objects.get_current()]
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def add_photos_to_current_site(modeladmin, request, queryset):
        current_site = Site.objects.get_current()
        current_site.photo_set.add(*queryset)
        msg = ngettext(
            'The photo has been successfully added to %(site)s',
            'The selected photos have been successfully added to %(site)s',
            len(queryset)
        ) % {'site': current_site.name}
        messages.success(request, msg)

    add_photos_to_current_site.short_description = \
        _("Add selected photos to the current site")

    def remove_photos_from_current_site(modeladmin, request, queryset):
        current_site = Site.objects.get_current()
        current_site.photo_set.remove(*queryset)
        msg = ngettext(
            'The photo has been successfully removed from %(site)s',
            'The selected photos have been successfully removed from %(site)s',
            len(queryset)
        ) % {'site': current_site.name}
        messages.success(request, msg)

    remove_photos_from_current_site.short_description = \
        _("Remove selected photos from the current site")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(r'^upload_zip/$',
                self.admin_site.admin_view(self.upload_zip),
                name='photologue_upload_zip')
        ]
        return custom_urls + urls

    def upload_zip(self, request):

        context = {
            'title': _('Upload a zip archive of photos'),
            'app_label': self.model._meta.app_label,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request)
        }

        # Handle form request
        if request.method == 'POST':
            form = UploadZipForm(request.POST, request.FILES)
            if form.is_valid():
                form.save(request=request)
                return HttpResponseRedirect('..')
        else:
            form = UploadZipForm()
        context['form'] = form
        context['adminform'] = helpers.AdminForm(form,
                                                 list([(None, {'fields': form.base_fields})]),
                                                 {})
        return render(request, 'admin/photologue/photo/upload_zip.html', context)


admin.site.register(Photo, PhotoAdmin)


class PhotoEffectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color', 'brightness',
                    'contrast', 'sharpness', 'filters', 'admin_sample')
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Adjustments', {
            'fields': ('color', 'brightness', 'contrast', 'sharpness')
        }),
        ('Filters', {
            'fields': ('filters',)
        }),
        ('Reflection', {
            'fields': ('reflection_size', 'reflection_strength', 'background_color')
        }),
        ('Transpose', {
            'fields': ('transpose_method',)
        }),
    )


admin.site.register(PhotoEffect, PhotoEffectAdmin)


class PhotoSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'width', 'height', 'crop', 'pre_cache', 'effect', 'increment_count')
    fieldsets = (
        (None, {
            'fields': ('name', 'width', 'height', 'quality')
        }),
        ('Options', {
            'fields': ('upscale', 'crop', 'pre_cache', 'increment_count')
        }),
        ('Enhancements', {
            'fields': ('effect', 'watermark',)
        }),
    )


admin.site.register(PhotoSize, PhotoSizeAdmin)


class WatermarkAdmin(admin.ModelAdmin):
    list_display = ('name', 'opacity', 'style')


admin.site.register(Watermark, WatermarkAdmin)

admin.site.register(Document)