from __future__ import unicode_literals
from django.db import models
from local_summernote.utils import get_attachment_storage, get_attachment_upload_to


__all__ = ['AbstractAttachment', 'Attachment', ]


class AbstractAttachment(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, help_text="Defaults to filename, if left blank")
    file = models.FileField(
        upload_to=get_attachment_upload_to(),
        storage=get_attachment_storage()
    )
    uploaded = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        abstract = True


class Attachment(AbstractAttachment):
    pass
