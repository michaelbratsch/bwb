from django.forms import ModelForm
from django.core.mail import send_mail

from register.models import Candidate

class CandidateForm(ModelForm):
    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'First name',
            'last_name' : 'Last name',
            'email'     : 'Email address'
        }

