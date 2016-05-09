from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, FormView
from django.views.generic.base import TemplateView
import random

from register.models import Candidate, Bicycle, HandoutEvent
from register.models import User_Registration, Invitation
from staff.forms import HandoverForm, EventForm, InviteForm, RefundForm
from staff.forms import ModifyCandidateForm, InviteCandidateForm


class ManageView(TemplateView):
    template_name = 'staff/index.html'


class EventOverviewView(TemplateView):
    template_name = 'staff/event_overview.html'


class CreateEventView(FormView):
    template_name = 'staff/create_event.html'
    form_class = EventForm
    success_url = reverse_lazy('staff:event_overview')

    def form_valid(self, form):
        due_date = form.cleaned_data['due_date']

        event = HandoutEvent.objects.create(due_date=due_date)

        self.success_url = reverse_lazy('staff:event',
                                        kwargs={'event_id': event.id})

        return super(FormView, self).form_valid(form)


class AutoInviteView(FormView):
    template_name = 'staff/invite.html'
    form_class = InviteForm
    success_url = reverse_lazy('staff:event_overview')

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


class CandidateMixin(object):

    def get(self, request, candidate_id, *args, **kwargs):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        context_dict = {'candidate': candidate}

        event_id = request.GET.get('event_id')
        if event_id is not None:
            event = get_object_or_404(HandoutEvent, id=event_id)
            context_dict['event'] = event
            context_dict['event_string'] = '?event_id=%s' % event.id

        return render(request, self.template_name, context_dict)

    def set_success_url(self, form):
        candidate_id = form.cleaned_data['candidate_id']
        if not Candidate.objects.filter(id=candidate_id):
            raise Http404("Candidate id not found.")
        self.success_url = reverse_lazy('staff:candidate',
                                        kwargs={'candidate_id': candidate_id})

        event_id = form.cleaned_data['event_id']
        if event_id:
            if not HandoutEvent.objects.filter(id=event_id):
                raise Http404("Event id not found.")
            self.success_url += '?event_id=%s' % event_id


class CandidateView(CandidateMixin, View):
    template_name = 'staff/candidate.html'


class ModifyCandidateView(CandidateMixin, FormView):
    template_name = 'staff/modify_candidate.html'
    form_class = ModifyCandidateForm

    def form_valid(self, form):
        candidate_id = form.cleaned_data['candidate_id']

        form_data = {'first_name': form.cleaned_data['first_name'],
                     'last_name': form.cleaned_data['last_name'],
                     'date_of_birth': form.cleaned_data['date_of_birth']}

        if Candidate.objects.exclude(id=candidate_id).filter(**form_data):
            raise Http404("This candidate already exists")

        Candidate.objects.filter(id=candidate_id).update(**form_data)

        self.set_success_url(form)

        return super(ModifyCandidateView, self).form_valid(form)


class HandoverBicycleView(CandidateMixin, FormView):
    template_name = 'staff/handover_bicycle.html'
    form_class = HandoverForm

    def form_valid(self, form):
        candidate_id = form.cleaned_data['candidate_id']

        candidate = get_object_or_404(Candidate, id=candidate_id)
        if candidate.has_bicycle:
            raise Http404("This Candidate already has a bicycle.")

        bicycle_number = form.cleaned_data['bicycle_number']
        lock_combination = form.cleaned_data['lock_combination']
        color = form.cleaned_data['color']
        brand = form.cleaned_data['brand']
        general_remarks = form.cleaned_data['general_remarks']
        Bicycle.objects.create(candidate=candidate,
                               bicycle_number=bicycle_number,
                               lock_combination=lock_combination,
                               color=color,
                               brand=brand,
                               general_remarks=general_remarks)

        self.set_success_url(form)

        return super(HandoverBicycleView, self).form_valid(form)


class RefundBicycleView(CandidateMixin, FormView):
    template_name = 'staff/refund_bicycle.html'
    form_class = RefundForm

    def form_valid(self, form):
        candidate_id = form.cleaned_data['candidate_id']

        candidate = get_object_or_404(Candidate, id=candidate_id)
        if not candidate.has_bicycle:
            raise Http404("This Candidate does not have a bicycle.")

        candidate.bicycle.delete()

        self.set_success_url(form)

        return super(RefundBicycleView, self).form_valid(form)


class InviteCandidateView(CandidateMixin, FormView):
    template_name = 'staff/invite_candidate.html'
    form_class = InviteCandidateForm

    def form_valid(self, form):
        candidate_id = form.cleaned_data['candidate_id']
        candidate = get_object_or_404(Candidate, id=candidate_id)

        invitation_event_id = form.cleaned_data['invitation_event_id']
        invitation_event = get_object_or_404(
            HandoutEvent, id=invitation_event_id)

        if invitation_event not in candidate.events_not_invited_to:
            raise Http404("The Candidate is already invited to this event.")

        Invitation.objects.create(candidate=candidate,
                                  handout_event=invitation_event)

        self.set_success_url(form)

        return super(InviteCandidateView, self).form_valid(form)
