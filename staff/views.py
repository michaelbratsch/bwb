from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic import View, FormView
from django.utils.dateparse import parse_datetime
from django.http import Http404

import random

from register.models import Candidate, Bicycle, Event, Winner
from staff.forms import HandoverForm, EventForm, CloseEventForm


class ManageView(TemplateView):
    template_name = 'staff/index.html'


class CreateEventView(FormView):
    template_name = 'staff/create_event.html'
    form_class = EventForm
    success_url = reverse_lazy('staff:index')

    def form_valid(self, form):
        date = form.cleaned_data['date']
        time = form.cleaned_data['time']
        date_time = parse_datetime('%s %s' % (date, time))

        max_registrations = form.cleaned_data['max_registrations']

        event = Event.objects.create(due_date=date_time,
                                     max_registrations=max_registrations)

        self.success_url = reverse_lazy('staff:event',
                                        kwargs={'event_id': event.id})

        return super(FormView, self).form_valid(form)


class CloseEventView(FormView):
    template_name = 'staff/close_event.html'
    form_class = CloseEventForm
    success_url = reverse_lazy('staff:index')

    def form_valid(self, form):
        number_of_winners = form.cleaned_data['number_of_winners']
        event_id = form.cleaned_data['event_id']

        event = get_object_or_404(Event, id=event_id)
        if event.is_closed:
            raise Http404('The event is already closed.')
        event.is_closed = True
        event.save()

        candidates = event.get_registered_candidates()

        winners = random.sample(candidates, min(len(candidates),
                                                number_of_winners))

        for winner in winners:
            Winner.objects.create(event=event, candidate=winner)

        self.success_url = reverse_lazy('staff:event',
                                        kwargs={'event_id': event.id})

        return super(FormView, self).form_valid(form)

    def get(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)

        context_dict = {'event': event}
        return render(request, self.template_name, context_dict)


class EventView(View):
    template_name = 'staff/event.html'

    def get(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)

        candidates = event.get_registered_candidates()

        context_dict = {'number_of_candidates': len(candidates),
                        'candidates': candidates,
                        'event': event}
        return render(request, self.template_name, context_dict)


class HandoverBicycleView(FormView):
    template_name = 'staff/handover_bicycle.html'
    form_class = HandoverForm
    success_url = reverse_lazy('staff')

    def form_valid(self, form):
        candidate_id = form.cleaned_data['candidate_id']
        bicycle_number = form.cleaned_data['bicycle_number']
        general_remarks = form.cleaned_data['general_remarks']

        candidate = get_object_or_404(Candidate, id=candidate_id)
        if not candidate.has_won:
            raise Http404("This Candidate has not won a bicycle.")
        if candidate.has_bicycle:
            raise Http404("This Candidate already has a bicycle.")

        Bicycle.objects.create(winner=candidate.winner,
                               bicycle_number=bicycle_number,
                               general_remarks=general_remarks)

        event = candidate.registration.event
        self.success_url = reverse_lazy('staff:event',
                                        kwargs={'event_id': event.id})

        return super(HandoverBicycleView, self).form_valid(form)

    def get(self, request, candidate_id, *args, **kwargs):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        event = candidate.registration.event

        context_dict = {'candidate': candidate,
                        'event': event}
        return render(request, self.template_name, context_dict)
