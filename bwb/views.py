from django.shortcuts import render
from django.views.generic import View


class GreetingsView(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        context_dict = {'show_steps': True}
        return render(request, self.template_name, context_dict)


class LegalView(View):
    template_name = 'legal.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
