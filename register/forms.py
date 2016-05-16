from django import forms

from register.models import max_name_length, User_Registration


class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=max_name_length, required=True)
    last_name = forms.CharField(max_length=max_name_length, required=True)
    date_of_birth = forms.DateField(required=True)

    email = forms.EmailField(required=True)
    bicycle_kind = forms.ChoiceField(
        choices=User_Registration.BICYCLE_CHOICES,
        required=True)
