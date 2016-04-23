from django.shortcuts import render, redirect
from django.utils import translation
from django.http import HttpResponseBadRequest
from django.views.generic import View

from bwb.settings import LANGUAGES
from register.models import Event


class GreetingsView(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        events = [event for event in Event.objects.all()
                  if not event.is_closed]
        events.sort(key=lambda x: x.due_date)
        context_dict = {'events': events}

        return render(request, self.template_name, context_dict)

    def post(self, request, *args, **kwargs):
        user_language = request.POST.get('language')

        if user_language not in [language for language, _ in LANGUAGES]:
            return HttpResponseBadRequest()

        translation.activate(user_language)
        request.session[translation.LANGUAGE_SESSION_KEY] = user_language

        return redirect('index')
