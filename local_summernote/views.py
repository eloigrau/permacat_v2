from django import VERSION as django_version
from django.templatetags.static import static
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from local_summernote.utils import get_attachment_model, using_config
try:
    # Django >= 1.10
    from django.views import View
except ImportError:
    from django.views.generic import View


class SummernoteEditor(TemplateView):
    template_name = 'local_summernote/widget_iframe_editor.html'

    @using_config
    def __init__(self):
        super(SummernoteEditor, self).__init__()
        self.css = \
             tuple([static(x) for x in config['base_css']])\
            + tuple([static(x) for x in config['codemirror_css'] if 'codemirror' in config]) \
            + tuple(static(x) for x in config['default_css']) \
            + tuple([static(x) for x in config['css']])

        self.js = \
             tuple([static(x) for x in config['base_js']])\
            + tuple([static(x) for x in config['codemirror_js'] if 'codemirror' in config]) \
            + tuple(static(x) for x in config['default_js'])\
            + tuple([static(x) for x in config['js']])

    @using_config
    def get_context_data(self, **kwargs):
        context = super(SummernoteEditor, self).get_context_data(**kwargs)

        context['id_src'] = self.kwargs['id']
        context['id'] = self.kwargs['id'].replace('-', '_')
        context['css'] = self.css
        context['js'] = self.js
        context['config'] = config

        return context


class SummernoteUploadAttachment(View):
    def __init__(self):
        super(SummernoteUploadAttachment, self).__init__()

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'false',
            'message': _('Only POST method is allowed'),
        }, status=400)

    @using_config
    def post(self, request, *args, **kwargs):
        authenticated = \
            request.user.is_authenticated if django_version >= (1, 10) \
            else request.user.is_authenticated()

        if config['attachment_require_authentication'] and \
                not authenticated:
            return JsonResponse({
                'status': 'false',
                'message': _('Only authenticated users are allowed'),
            }, status=403)

        if not request.FILES.getlist('files'):
            return JsonResponse({
                'status': 'false',
                'message': _('No files were requested'),
            }, status=400)

        # remove unnecessary CSRF token, if found
        kwargs = request.POST.copy()
        kwargs.pop("csrfmiddlewaretoken", None)

        try:
            attachments = []

            for file in request.FILES.getlist('files'):

                # create instance of appropriate attachment class
                klass = get_attachment_model()
                attachment = klass()

                attachment.file = file
                attachment.name = file.name

                if file.size > config['attachment_filesize_limit']:
                    return JsonResponse({
                        'status': 'false',
                        'message': _('File size exceeds the limit allowed and cannot be saved'),
                    }, status=400)

                # calling save method with attachment parameters as kwargs
                attachment.save(**kwargs)
                attachments.append(attachment)

            return HttpResponse(render_to_string('local_summernote/upload_attachment.json', {
                'attachments': attachments,
            }), content_type='application/json')
        except IOError:
            return JsonResponse({
                'status': 'false',
                'message': _('Failed to save attachment'),
            }, status=500)
