
from django.urls import path, include, re_path

from local_summernote.views import (
    SummernoteEditor, SummernoteUploadAttachment
)

urlpatterns = [
    re_path(r'^editor/(?P<id>.+)/$', SummernoteEditor.as_view(),
        name='local_summernote-editor'),
    re_path(r'^upload_attachment/$', SummernoteUploadAttachment.as_view(),
        name='local_summernote-upload_attachment'),
]
