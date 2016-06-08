from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, FormView
from django.views.generic.base import TemplateView
from django_tables2 import RequestConfig
import random

from register.email import send_message_after_invitation
from register.models import Candidate, Bicycle, HandoutEvent
from register.models import UserRegistration, Invitation
from staff.forms import CreateCandidateForm, DeleteCandidateForm
from staff.forms import HandoverForm, EventForm, InviteForm, RefundForm
from staff.forms import ModifyCandidateForm, InviteCandidateForm
from staff.tables import CandidateTable, BicycleTable, EventTable


class ManageView(TemplateView):
    template_name = 'staff/index.html'


class BicycleOverviewView(View):
    template_name = 'staff/bicycle_overview.html'

    def get(self, request, *args, **kwargs):
        queryset = Bicycle.objects.all()
        table = BicycleTable(queryset)
        RequestConfig(request, paginate={'per_page': 40}).configure(table)

        context_dict = {'bicycles': table}
        return render(request, self.template_name, context_dict)


class EventOverviewView(TemplateView):
    template_name = 'staff/event_overview.html'


class CreateEventView(FormView):
    template_name = 'staff/create_event.html'
    form_class = EventForm
    success_url = reverse_lazy('staff:event_overview')

    def form_valid(self, form):
        due_date = form.cleaned_data['due_date']

        if HandoutEvent.objects.filter(due_date=due_date):
            raise Http404("An event on that time and date already exists.")

        event = HandoutEvent.objects.create(due_date=due_date)

        self.success_url = reverse_lazy('staff:event',
                                        kwargs={'event_id': event.id})

        return super(CreateEventView, self).form_valid(form)


class AutoInviteView(FormView):
    template_name = 'staff/auto_invite.html'
    form_class = InviteForm
    success_url = reverse_lazy('staff:event_overview')

    def form_valid(self, form):
        event_id = form.cleaned_data['event_id']

        event = get_object_or_404(HandoutEvent, id=event_id)

        for choice, _ in UserRegistration.BICYCLE_CHOICES:
            number_of_winners = form.cleaned_data['choice_%s' % choice]

            # do have no bicycle and are registered with contact information
            candidate = Candidate.registered_and_without_bicycle(choice)

            # are not invited yet
            candidate = [c for c in candidate if c.invitations.count() == 0]

            winners = random.sample(candidate, min(len(candidate),
                                                   number_of_winners))

            for winner in winners:
                Invitation.objects.create(handout_event=event,
                                          candidate=winner)

                send_message_after_invitation(candidate=winner,
                                              handout_event=event)

        self.success_url = reverse_lazy('staff:event',
                                        kwargs={'event_id': event.id})

        return super(AutoInviteView, self).form_valid(form)

    def get(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(HandoutEvent, id=event_id)

        context_dict = {'event': event,
                        'bike_choices': UserRegistration.BICYCLE_CHOICES}
        return render(request, self.template_name, context_dict)


class EventView(View):
    template_name = 'staff/event.html'

    def get(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(HandoutEvent, id=event_id)

        invited_candidates = [
            invitation.candidate.id for invitation in event.invitations.all()
        ]

        queryset = Candidate.objects.filter(id__in=invited_candidates)
        candidate_table = EventTable(data=queryset, event_id=event_id)
        RequestConfig(request, paginate={'per_page': 100}).configure(
            candidate_table)

        context_dict = {
            'number_of_candidates': len(invited_candidates),
            'candidate_table': candidate_table,
            'event': event}
        return render(request, self.template_name, context_dict)


class CandidateOverviewView(View):
    template_name = 'staff/candidate_overview.html'
    query_set = None

    def get(self, request, *args, **kwargs):
        candidates_table = CandidateTable(self.query_set)
        RequestConfig(request, paginate={'per_page': 40}).configure(
            candidates_table)

        context_dict = {'candidate': Candidate.objects.all(),
                        'candidates_table': candidates_table}
        return render(request, self.template_name, context_dict)


class CreateCandidateView(FormView):
    template_name = 'staff/create_candidate.html'
    form_class = CreateCandidateForm
    success_url = reverse_lazy('staff:candidate_overview')

    def form_valid(self, form):
        form_data = {'first_name': form.cleaned_data['first_name'],
                     'last_name': form.cleaned_data['last_name'],
                     'date_of_birth': form.cleaned_data['date_of_birth']}

        if Candidate.get_matching(**form_data):
            raise Http404("This candidate already exists")

        Candidate.objects.create(**form_data)

        return super(CreateCandidateView, self).form_valid(form)


class CandidateMixin(object):

    def get_context_dict(self, candidate_id, event_id, bicycle_id, data=None):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        context_dict = {'candidate': candidate,
                        'base_template_name': 'staff/base_candidate_view.html'}

        if event_id:
            event = get_object_or_404(HandoutEvent, id=event_id)
            context_dict['event'] = event
            context_dict['base_template_name'] = 'staff/base_event_view.html'
        elif bicycle_id:
            bicycle = get_object_or_404(Bicycle, id=bicycle_id)
            context_dict['bicycle'] = bicycle
            context_dict['base_template_name'] = 'staff/base_bicycle_view.html'

        if self.form_class:
            context_dict['form'] = self.form_class(
                data=data,
                candidate_id=candidate_id,
                event_id=event_id,
                bicycle_id=bicycle_id)

        return context_dict

    def get(self, request, candidate_id):
        event_id = request.GET.get('event_id')
        bicycle_id = request.GET.get('bicycle_id')

        context_dict = self.get_context_dict(candidate_id=candidate_id,
                                             event_id=event_id,
                                             bicycle_id=bicycle_id)

        return render(request, self.template_name, context_dict)

    def post(self, request, candidate_id):
        event_id = request.POST.get('event_id')
        bicycle_id = request.POST.get('bicycle_id')

        context_dict = self.get_context_dict(candidate_id=candidate_id,
                                             event_id=event_id,
                                             bicycle_id=bicycle_id,
                                             data=request.POST)

        form = context_dict['form']

        if form.is_valid():
            self.form_valid(form)
            return HttpResponseRedirect(self.success_url)

        return render(request, self.template_name, context_dict)

    def set_success_url(self, form):
        candidate_id = form.cleaned_data['candidate_id']
        if not Candidate.objects.filter(id=candidate_id):
            raise Http404("Candidate id not found.")
        self.success_url = reverse_lazy('staff:candidate',
                                        kwargs={'candidate_id': candidate_id})

        event_id = form.cleaned_data.get('event_id')
        bicycle_id = form.cleaned_data.get('bicycle_id')
        if event_id:
            event = get_object_or_404(HandoutEvent, id=event_id)
            self.success_url += event.url_parameter
        elif bicycle_id:
            try:
                bicycle = Bicycle.objects.get(id=bicycle_id)
                self.success_url += bicycle.url_parameter
            except Bicycle.DoesNotExist:
                # the bicycle has been handed back
                self.success_url = reverse_lazy('staff:bicycle_overview')


class CandidateView(CandidateMixin, View):
    template_name = 'staff/candidate.html'
    form_class = None


class DeleteCandidateView(CandidateMixin, FormView):
    template_name = 'staff/delete_candidate.html'
    form_class = DeleteCandidateForm

    def form_valid(self, form):
        candidate_id = form.cleaned_data['candidate_id']
        candidate = get_object_or_404(Candidate, id=candidate_id)
        candidate.delete()

        event_id = form.cleaned_data.get('event_id')
        bicycle_id = form.cleaned_data.get('bicycle_id')
        if event_id:
            self.success_url = reverse_lazy('staff:event',
                                            kwargs={'event_id': event_id})
        elif bicycle_id:
            self.success_url = reverse_lazy('staff:bicycle_overview')
        else:
            self.success_url = reverse_lazy('staff:candidate_overview')

        return super(DeleteCandidateView, self).form_valid(form)


class ModifyCandidateView(CandidateMixin, FormView):
    template_name = 'staff/modify_candidate.html'
    form_class = ModifyCandidateForm

    def form_valid(self, form):
        candidate_id = form.cleaned_data['candidate_id']

        form_data = {'first_name': form.cleaned_data['first_name'],
                     'last_name': form.cleaned_data['last_name'],
                     'date_of_birth': form.cleaned_data['date_of_birth']}

        if Candidate.get_matching(**form_data).exclude(id=candidate_id):
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

        send_message_after_invitation(candidate=candidate,
                                      handout_event=invitation_event)

        self.set_success_url(form)

        return super(InviteCandidateView, self).form_valid(form)
