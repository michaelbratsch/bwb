from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.views.generic.edit import FormView

from register.forms import RegistrationForm
from register.models import Registration, Candidate
from register.email import send_register_email


class ContactView(FormView):
    template_name = 'register/index.html'
    form_class = RegistrationForm
    success_url = 'thanks.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']

        # Create and save registration and candidate object
        registration = Registration.objects.create(email=email)
        candidate = Candidate.objects.create(registration=registration,
                                             first_name=first_name,
                                             last_name=last_name)

        recipient = {'email': registration.email,
                     'name': '%s %s' % (candidate.first_name,
                                        candidate.last_name),
                     'identifier': candidate.identifier}
        base_url = '{scheme}://{host}'.format(scheme=self.request.scheme,
                                              host=self.request.get_host())
        send_register_email(recipient=recipient,
                            base_url=base_url)

        return super(ContactView, self).form_valid(form)


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

        candidate = get_object_or_404(Candidate, identifier=identifier)
        registration = candidate.registration
        registration.validate_email()

        context_dict = {'number_in_line': candidate.number_in_line()}
        return render(request, self.template_name, context_dict)
