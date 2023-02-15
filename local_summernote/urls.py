from django.conf.urls import url

from local_summernote.views import (
    SummernoteEditor, SummernoteUploadAttachment
)

urlpatterns = [
    url(r'^editor/(?P<id>.+)/$', SummernoteEditor.as_view(),
        name='local_summernote-editor'),
    url(r'^upload_attachment/$', SummernoteUploadAttachment.as_view(),
        name='local_summernote-upload_attachment'),
]
