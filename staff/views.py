from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views.generic import View

from register.models import Candidate


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
            raise Http404("User has already a bicycle.")

        context_dict = {'first_name': candidate.first_name,
                        'last_name': candidate.last_name}
        return render(request, self.template_name, context_dict)
