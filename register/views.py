from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.views.generic.edit import FormView

from register.forms import CandidateForm
from register.models import CandidateMetaData
from register.email import send_register_email


class ContactView(FormView):
    template_name = 'register/index.html'
    form_class = CandidateForm
    success_url = 'thanks.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        # Save name and email address
        candidate = form.save(commit=True)

        # Create meta data and save it
        meta_data = CandidateMetaData.objects.create(candidate=candidate)

        recipient = {'email': candidate.email,
                     'name': '%s %s' % (candidate.first_name,
                                        candidate.last_name),
                     'identifier': meta_data.identifier}
        base_url = '{scheme}://{host}'.format(scheme=self.request.scheme,
                                              host=self.request.get_host())
        send_register_email(recipient=recipient,
                            base_url=base_url)

        return super(ContactView, self).form_valid(form)


class ThanksView(View):
    template_name = 'register/thanks.html'

    def get(self, request, *args, **kwargs):
        context_dict = {'number_in_line':
                        CandidateMetaData.candidates_in_line()}
        return render(request, self.template_name, context_dict)


class CurrentInLineView(View):
    template_name = 'register/current_in_line.html'

    def get(self, request, *args, **kwargs):
        identifier = request.GET.get('user_id')

        candidate = get_object_or_404(CandidateMetaData, identifier=identifier)
        candidate.validate_email()

        context_dict = {'number_in_line': candidate.number_in_line()}
        return render(request, self.template_name, context_dict)
