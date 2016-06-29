from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import get_language
from django.views.generic import View
from django.views.generic.edit import FormView

from register.email import send_message_after_registration
from register.forms import RegistrationForm, open_for_registration
from register.forms import TOO_MANY_REGISTRATIONS_ERROR
from register.models import UserRegistration, Candidate


class GreetingsView(View):
    template_name = 'register/greeting.html'

    def get(self, request, *args, **kwargs):
        context_dict = {'open_for_registration': open_for_registration(),
                        'too_many_registrations_error': TOO_MANY_REGISTRATIONS_ERROR,
                        'show_steps': True,
                        'step_1': 'class="active"'}
        return render(request, self.template_name, context_dict)


class RegistrationView(FormView):
    template_name = 'register/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        assert open_for_registration(), TOO_MANY_REGISTRATIONS_ERROR

        form_data = {
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'date_of_birth': form.cleaned_data['date_of_birth']}

        candidate = Candidate.objects.create(**form_data)

        creation_dict = {'candidate': candidate,
                         'bicycle_kind': form.cleaned_data['bicycle_kind'],
                         'language': get_language()}

        email = form.cleaned_data['email']
        mobile_number = form.cleaned_data['mobile_number']

        assert email or mobile_number, ("Neither email nor mobile phone "
                                        "number are given.")

        if email:
            creation_dict['email'] = email
        if mobile_number:
            creation_dict['mobile_number'] = mobile_number

        registration = UserRegistration.objects.create(**creation_dict)

        send_message_after_registration(registration=registration,
                                        request=self.request)

        self.success_url = reverse_lazy(
            'register:thanks',
            kwargs={'user_id': registration.identifier})

        return super(RegistrationView, self).form_valid(form)

    def form_invalid(self, form):
        return super(RegistrationView, self).form_invalid(form)

    def get(self, request, *args, **kwargs):

        context_dict = {'open_for_registration': open_for_registration(),
                        'too_many_registrations_error': TOO_MANY_REGISTRATIONS_ERROR,
                        'choices': UserRegistration.BICYCLE_CHOICES,
                        'show_steps': True,
                        'step_2': 'class="active"',
                        'form': RegistrationForm()}
        return render(request, self.template_name, context_dict)


class ThanksView(View):
    template_name = 'register/thanks.html'

    def get(self, request, user_id, *args, **kwargs):
        registration = get_object_or_404(
            UserRegistration, identifier=user_id)

        context_dict = {
            'show_steps': True,
            'step_3': 'class="active"',
            'registration': registration}
        return render(request, self.template_name, context_dict)


class CurrentInLineView(View):
    template_name = 'register/current_in_line.html'

    def get(self, request, user_id, *args, **kwargs):
        registration = get_object_or_404(
            UserRegistration, identifier=user_id)

        first_time = not registration.email_validated
        registration.validate_email()

        context_dict = {'first_time': first_time,
                        'registration': registration}
        return render(request, self.template_name, context_dict)
