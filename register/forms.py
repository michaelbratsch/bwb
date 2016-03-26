from django import forms

from register.models import max_name_length


class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=max_name_length)
    last_name = forms.CharField(max_length=max_name_length)
    email = forms.EmailField()

    class Meta:
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Email address'
        }
