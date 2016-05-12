from django import forms

from register.models import max_name_length, User_Registration


class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=max_name_length)
    last_name = forms.CharField(max_length=max_name_length)
    date_of_birth = forms.DateField()

    email = forms.EmailField()
    bicycle_kind = forms.ChoiceField(
        choices=User_Registration.BICYCLE_CHOICES)
