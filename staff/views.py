from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, FormView
from django.views.generic.base import TemplateView
import random

from register.models import Candidate, Bicycle, HandoutEvent, \
    User_Registration, Invitation
from staff.forms import HandoverForm, EventForm, InviteForm


class ManageView(TemplateView):
    template_name = 'staff/index.html'


class CreateEventView(FormView):
    template_name = 'staff/create_event.html'
    form_class = EventForm
    success_url = reverse_lazy('staff:index')

    def form_valid(self, form):
        due_date = form.cleaned_data['due_date']

        event = HandoutEvent.objects.create(due_date=due_date)

        self.success_url = reverse_lazy('staff:event',
                                        kwargs={'event_id': event.id})

        return super(FormView, self).form_valid(form)


class InviteView(FormView):
    template_name = 'staff/invite.html'
    form_class = InviteForm
    success_url = reverse_lazy('staff:index')

    def form_valid(self, form):
        event_id = form.cleaned_data['event_id']

        event = get_object_or_404(HandoutEvent, id=event_id)

        for choice, _ in User_Registration.BICYCLE_CHOICES:
            number_of_winners = form.cleaned_data['choice_%s' % choice]

            candidates = list(Candidate.waiting_for_bicycle(choice))

            winners = random.sample(candidates, min(len(candidates),
                                                    number_of_winners))

            for winner in winners:
                Invitation.objects.create(handout_event=event,
                                          candidate=winner)

        self.success_url = reverse_lazy('staff:event',
                                        kwargs={'event_id': event.id})

        return super(FormView, self).form_valid(form)

    def get(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(HandoutEvent, id=event_id)

        context_dict = {'event': event,
                        'bike_choices': User_Registration.BICYCLE_CHOICES}
        return render(request, self.template_name, context_dict)


class EventView(View):
    template_name = 'staff/event.html'

    def get_candidates_in_groups(self, all_candidates):
        for choice, description in User_Registration.BICYCLE_CHOICES:
            yield (description,
                   filter(lambda c: c.user_registration.bicycle_kind == choice,
                          all_candidates))

    def get(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(HandoutEvent, id=event_id)

        all_candidates = [
            invitation.candidate for invitation in event.invitations.all()]

        context_dict = {
            'total_number_of_candidates': len(all_candidates),
            'candidate_groups': self.get_candidates_in_groups(all_candidates),
            'event': event}
        return render(request, self.template_name, context_dict)


class CandidateOverviewView(View):
    template_name = 'staff/candidate_overview.html'

    def get(self, request, *args, **kwargs):
        context_dict = {'candidates': Candidate.objects.all()}
        return render(request, self.template_name, context_dict)


def append_event(request, context_dict):
    event_id = request.GET.get('event_id')
    if event_id is not None:
        event = get_object_or_404(HandoutEvent, id=event_id)
        context_dict['event'] = event
        context_dict['event_string'] = '?event_id=%s' % event.id


class CandidateView(View):
    template_name = 'staff/candidate.html'

    def get(self, request, candidate_id, *args, **kwargs):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        context_dict = {'candidate': candidate}

        append_event(request, context_dict)

        return render(request, self.template_name, context_dict)


class ModifyCandidateView(View):
    template_name = 'staff/modify_candidate.html'

    def get(self, request, candidate_id, *args, **kwargs):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        context_dict = {'candidate': candidate}

        append_event(request, context_dict)

        return render(request, self.template_name, context_dict)


class HandoverBicycleView(FormView):
    template_name = 'staff/handover_bicycle.html'
    form_class = HandoverForm
    success_url = reverse_lazy('staff')

    def form_valid(self, form):
        event_id = form.cleaned_data['event_id']
        candidate_id = form.cleaned_data['candidate_id']
        bicycle_number = form.cleaned_data['bicycle_number']
        lock_combination = form.cleaned_data['lock_combination']
        color = form.cleaned_data['color']
        brand = form.cleaned_data['brand']
        general_remarks = form.cleaned_data['general_remarks']

        candidate = get_object_or_404(Candidate, id=candidate_id)
        if candidate.has_bicycle:
            raise Http404("This Candidate already has a bicycle.")

        Bicycle.objects.create(candidate=candidate,
                               bicycle_number=bicycle_number,
                               lock_combination=lock_combination,
                               color=color,
                               brand=brand,
                               general_remarks=general_remarks)

        self.success_url = reverse_lazy('staff:event',
                                        kwargs={'event_id': event_id})

        return super(HandoverBicycleView, self).form_valid(form)

    def get(self, request, candidate_id, *args, **kwargs):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        context_dict = {'candidate': candidate}

        append_event(request, context_dict)

        return render(request, self.template_name, context_dict)
