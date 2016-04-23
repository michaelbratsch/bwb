from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.views.generic.edit import FormView
from django.utils.translation import ugettext

from register.forms import RegistrationForm
from register.models import Registration, Candidate, Event
from register.email import send_register_email
from django.core.urlresolvers import reverse_lazy


class ContactView(FormView):
    template_name = 'register/index.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('register:thanks')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        event_id = form.cleaned_data['event_id']

        event = get_object_or_404(Event, id=event_id)

        # Create and save registration and candidate object
        registration = Registration.objects.create(event=event,
                                                   email=email)

        for i in range(5):
            first_name = form.cleaned_data['first_name_%s' % i]
            last_name = form.cleaned_data['last_name_%s' % i]
            if first_name and last_name:
                Candidate.objects.create(registration=registration,
                                         first_name=first_name,
                                         last_name=last_name)

        names = ["%s %s" % (c.first_name, c.last_name)
                 for c in registration.candidates.all()]

        name_link = " " + ugettext('and') + " "
        recipient = {'email': registration.email,
                     'name': name_link.join(names),
                     'identifier': registration.identifier}

        base_url = '{scheme}://{host}'.format(scheme=self.request.scheme,
                                              host=self.request.get_host())
        send_register_email(recipient=recipient,
                            base_url=base_url)

        return super(ContactView, self).form_valid(form)

    def get(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)

        context_dict = {'event': event}

        return render(request, self.template_name, context_dict)


class ThanksView(View):
    template_name = 'register/thanks.html'

    def get(self, request, *args, **kwargs):
        context_dict = {'number_in_line':
                        Candidate.total_in_line()}
        return render(request, self.template_name, context_dict)


class CurrentInLineView(View):
    template_name = 'register/current_in_line.html'

    def get(self, request, *args, **kwargs):
        identifier = request.GET.get('user_id')

        registration = get_object_or_404(Registration, identifier=identifier)
        registration.validate_email()

        context_dict = {'number_in_line': registration.number_in_line()}
        return render(request, self.template_name, context_dict)
