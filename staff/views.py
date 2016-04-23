from django.shortcuts import render, get_object_or_404
from django.views.generic import View, FormView
from django.http import Http404

from register.models import Candidate, Bicycle
from staff.forms import HandoverForm
from django.core.urlresolvers import reverse_lazy


class ManageView(View):
    template_name = 'staff/index.html'

    def get(self, request, *args, **kwargs):
        waiting_candidates = [(cand.first_name, cand.last_name, cand.id)
                              for cand in Candidate.without_bicycle()]

        context_dict = {'waiting_candidates': waiting_candidates}
        return render(request, self.template_name, context_dict)


class HandoverView(FormView):
    template_name = 'staff/handover.html'
    form_class = HandoverForm
    success_url = reverse_lazy('staff')

    def form_valid(self, form):
        candidate_id = form.cleaned_data['candidate_id']
        bicycle_number = form.cleaned_data['bicycle_number']
        general_remarks = form.cleaned_data['general_remarks']

        candidate = get_object_or_404(Candidate, id=candidate_id)
        if candidate.has_bicycle():
            raise Http404("This Candidate already has a bicycle.")

        Bicycle.objects.create(candidate=candidate,
                               bicycle_number=bicycle_number,
                               general_remarks=general_remarks)

        return super(HandoverView, self).form_valid(form)

    def get(self, request, candidate_id, *args, **kwargs):
        candidate = get_object_or_404(Candidate, id=candidate_id)

        context_dict = {'first_name': candidate.first_name,
                        'last_name': candidate.last_name,
                        'candidate_id': candidate.id}
        return render(request, self.template_name, context_dict)
