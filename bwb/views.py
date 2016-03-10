from django.shortcuts import render
from django.views.generic import View


class GreetingsView(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
