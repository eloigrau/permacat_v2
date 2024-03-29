from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin import widgets
from django.db import models
from local_summernote.utils import get_attachment_model, using_config
from local_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget


class SummernoteModelAdminMixin(object):
    summernote_fields = '__all__'

    @using_config
    def formfield_for_dbfield(self, db_field, *args, **kwargs):
        summernote_widget = SummernoteWidget if config['iframe'] else SummernoteInplaceWidget

        if self.summernote_fields == '__all__':
            if isinstance(db_field, models.TextField):
                kwargs['widget'] = summernote_widget
        else:
            if db_field.name in self.summernote_fields:
                kwargs['widget'] = summernote_widget

        return super(SummernoteModelAdminMixin, self).formfield_for_dbfield(db_field, *args, **kwargs)


class SummernoteInlineModelAdmin(SummernoteModelAdminMixin, InlineModelAdmin):
    pass


class SummernoteModelAdmin(SummernoteModelAdminMixin, admin.ModelAdmin):
    pass


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'file', 'uploaded']
    search_fields = ['name']
    ordering = ('-id',)

    def save_model(self, request, obj, form, change):
        obj.name = obj.file.name if (not obj.name) else obj.name
        super(AttachmentAdmin, self).save_model(request, obj, form, change)


admin.site.register(get_attachment_model(), AttachmentAdmin)
