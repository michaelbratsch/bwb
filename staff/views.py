from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.views.generic import View
from django.contrib.auth import authenticate, login

from register.models import Candidate
from staff.forms import LoginForm


class LoginView(View):
    template_name = 'staff/login.html'

    def get(self, request, *args, **kwags):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('staff:index')
                else:
                    raise Http404("The password is valid, but the account has"
                                  " been disabled!")
        raise Http404("Entered login credentials are not valid.")


class ManageView(View):
    template_name = 'staff/index.html'

    def get(self, request, *args, **kwargs):
        candidate_objects = Candidate.objects.filter(
            received_bicycle=False).all()

        waiting_candidates = [(cand.first_name, cand.last_name, cand.id)
                              for cand in candidate_objects]

        context_dict = {'waiting_candidates': waiting_candidates}
        return render(request, self.template_name, context_dict)


class HandoverView(View):
    template_name = 'staff/handover.html'

    def get(self, request, user_id, *args, **kwargs):
        candidate = get_object_or_404(Candidate, id=user_id)

        if candidate.received_bicycle:
            raise Http404("User already has a bicycle.")

        context_dict = {'first_name': candidate.first_name,
                        'last_name': candidate.last_name}
        return render(request, self.template_name, context_dict)
