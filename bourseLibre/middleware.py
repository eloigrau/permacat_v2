# from django.utils.timezone import now
# from .models import Profil
#
# class SetLastVisitMiddleware(object):
#     def process_response(self, request, response):
#         if request.user.is_authenticated():
#             # Update last visit time after request finished processing.
#             Profil.objects.filter(pk=request.user.pk).update(last_visit=now())
#         return response
from django.shortcuts import render
from django.core.exceptions import RequestDataTooBig
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from .settings import LANGUAGE_CODE

class CheckRequest(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            body = request.body
        except RequestDataTooBig:
            return render(request, "513.html")

        return self.get_response(request)

class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        try:
            if request.user.is_authenticated:
                translation.activate(request.user.language)
                request.LANGUAGE_CODE = request.user.language
        except:
            request.LANGUAGE_CODE = LANGUAGE_CODE

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response