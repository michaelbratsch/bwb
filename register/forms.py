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

    def send_email(self, identifier):

        lines = ("Hello %(first_name)s %(last_name)s,\n" % self.data,
                 "Thank you for registering for a bike.",
                 "To verify your email address and to check your current "
                 "number in line, please click the following link:",
                 "http://michaelbratsch/pythonanywhere.com/register/"
                 "current-in-line.html?user_id=%s" % str(identifier),
                 "\nWe hope to see you soon!")

        message = "\n".join(lines)

        send_mail(subject        = 'Bwb - Registration',
                  message        = message,
                  from_email     = 'foobar@gmail.com',
                  recipient_list = [self.data['email']],
                  fail_silently  = False)
