from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic import View, FormView
from django.utils.dateparse import parse_datetime
from django.http import Http404

from register.models import Candidate, Bicycle, Event
from staff.forms import HandoverForm, EventForm


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

        Event.objects.create(due_date=date_time)

        return super(FormView, self).form_valid(form)


class EventView(View):
    template_name = 'staff/event.html'

    def get(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)

        registrations = event.registrations.all()

        all_candidates = []
        for registration in registrations:
            all_candidates += registration.candidates.all()

        waiting_candidates = [cand for cand in all_candidates
                              if not cand.has_bicycle()]

        context_dict = {'all_candidates': all_candidates,
                        'waiting_candidates': waiting_candidates,
                        'event': event}
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

        event = candidate.registration.event
        self.success_url = reverse_lazy('staff:event',
                                        kwargs={'event_id': event.id})

        return super(HandoverView, self).form_valid(form)

    def get(self, request, candidate_id, *args, **kwargs):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        event = candidate.registration.event

        context_dict = {'candidate': candidate,
                        'event': event}
        return render(request, self.template_name, context_dict)
