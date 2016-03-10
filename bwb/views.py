from django.shortcuts import render, redirect
from django.utils import translation
from django.http import HttpResponseBadRequest
from django.views.generic import View

from bwb.settings import LANGUAGES


class GreetingsView(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        user_language = request.POST.get('language')

        if user_language not in [language for language, _ in LANGUAGES]:
            return HttpResponseBadRequest()

        translation.activate(user_language)
        request.session[translation.LANGUAGE_SESSION_KEY] = user_language

        return redirect('index')
