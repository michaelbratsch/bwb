from django.shortcuts import render
from django.views.generic import View
from django.views.generic.edit import FormView
from django.utils import timezone
from django.http import HttpResponseBadRequest

from register.forms import CandidateForm
from register.models import Candidate, CandidateMetaData

class ContactView(FormView):
    template_name = 'register/index.html'
    form_class = CandidateForm
    success_url = 'thanks.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        # Save name and email address
        new_candidate = form.save(commit=True)

        # Create meta data and save it
        meta_data = CandidateMetaData.create(candidate=new_candidate)
        meta_data.save()

        form.send_email(meta_data.identifier)

        return super(ContactView, self).form_valid(form)


class ThanksView(View):
    template_name = 'register/thanks.html'

    def get(self, request, *args, **kwargs):
        context_dict = {'number_in_line' : Candidate.objects.count()}
        return render(request, self.template_name, context_dict)

class CurrentInLineView(View):
    template_name = 'register/current_in_line.html'

    def get_matching_candidate(self, identifier):
        all_candidates = CandidateMetaData.objects.all()
        return [(i+1, x) for i, x in enumerate(all_candidates)
                if x.identifier == identifier]


    def get(self, request, *args, **kwargs):
        identifier = request.GET.get('user_id')

        if identifier:
            matching_candidates = self.get_matching_candidate(identifier)

            if len(matching_candidates) == 1:
                number_in_line, candidate = matching_candidates[0]

                if not candidate.email_validated:
                    candidate.email_validated = True
                    candidate.time_of_email_validation = timezone.now()
                    candidate.save()

                return render(request, self.template_name,
                              {'number_in_line' : number_in_line})

        return HttpResponseBadRequest()

