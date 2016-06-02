from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.views.generic.edit import FormView

from django.utils.translation import get_language

from register.email import send_message_after_registration
from register.forms import RegistrationForm, open_for_registration
from register.forms import too_many_registrations_error
from register.models import User_Registration, Candidate


class GreetingsView(View):
    template_name = 'register/greeting.html'

    def get(self, request, *args, **kwargs):
        context_dict = {'open_for_registration': open_for_registration(),
                        'show_steps': True,
                        'step_1': 'class="active"'}
        return render(request, self.template_name, context_dict)


class RegistrationView(FormView):
    template_name = 'register/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        assert open_for_registration(), too_many_registrations_error

        form_data = {
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'date_of_birth': form.cleaned_data['date_of_birth']}

        candidate = Candidate.objects.create(**form_data)

        creation_dict = {'candidate': candidate,
                         'bicycle_kind': form.cleaned_data['bicycle_kind'],
                         'language': get_language()}

        email = form.cleaned_data['email']
        phone_number = form.cleaned_data['phone_number']

        assert email or phone_number, ("Neither email nor phone number "
                                       "are given.")

        if email:
            creation_dict['email'] = email
        if phone_number:
            creation_dict['phone_number'] = phone_number

        registration = User_Registration.objects.create(**creation_dict)

        send_message_after_registration(registration=registration,
                                        request=self.request)

        self.success_url = reverse_lazy(
            'register:thanks',
            kwargs={'user_id': registration.identifier})

        return super(RegistrationView, self).form_valid(form)

    def form_invalid(self, form):
        return super(RegistrationView, self).form_invalid(form)

    def get(self, request, *args, **kwargs):
        if not open_for_registration():
            raise Http404(too_many_registrations_error)

        context_dict = {'choices': User_Registration.BICYCLE_CHOICES,
                        'show_steps': True,
                        'step_2': 'class="active"',
                        'form': RegistrationForm()}
        return render(request, self.template_name, context_dict)


class ThanksView(View):
    template_name = 'register/thanks.html'

    def get(self, request, user_id, *args, **kwargs):
        registration = get_object_or_404(
            User_Registration, identifier=user_id)
        registration.validate_email()

        context_dict = {
            'show_steps': True,
            'step_3': 'class="active"',
            'registration': registration,
            'bicycle_kind': registration.get_bicycle_kind_display()}
        return render(request, self.template_name, context_dict)


class CurrentInLineView(View):
    template_name = 'register/current_in_line.html'

    def get(self, request, user_id, *args, **kwargs):
        registration = get_object_or_404(
            User_Registration, identifier=user_id)
        registration.validate_email()

        context_dict = {
            'already_viewed': registration.email_validated,
            'number_in_line': registration.number_in_line(),
            'bicycle_kind': registration.get_bicycle_kind_display()}
        return render(request, self.template_name, context_dict)
