from django import forms
from django.utils.translation import ugettext

from register.models import max_name_length, User_Registration


class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=max_name_length, required=True)
    last_name = forms.CharField(max_length=max_name_length, required=True)
    date_of_birth = forms.DateField(required=True)

    email = forms.EmailField(required=False)
    mobile_number = forms.CharField(max_length=15, required=False)

    bicycle_kind = forms.ChoiceField(
        choices=User_Registration.BICYCLE_CHOICES,
        required=True)

    def clean(self):
        email = self.cleaned_data.get('email')
        mobile_number = self.cleaned_data.get('mobile_number')

        if not (email or mobile_number):
            raise forms.ValidationError(ugettext(
                "Either a email address or a mobile number is required for \
                 contacting you!"))

        return self.cleaned_data
