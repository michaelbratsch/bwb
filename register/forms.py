from django import forms

from register.models import max_name_length


class RegistrationForm(forms.Form):
    first_name_0 = forms.CharField(max_length=max_name_length)
    last_name_0 = forms.CharField(max_length=max_name_length)
    first_name_1 = forms.CharField(max_length=max_name_length, required=False)
    last_name_1 = forms.CharField(max_length=max_name_length, required=False)
    first_name_2 = forms.CharField(max_length=max_name_length, required=False)
    last_name_2 = forms.CharField(max_length=max_name_length, required=False)
    first_name_3 = forms.CharField(max_length=max_name_length, required=False)
    last_name_3 = forms.CharField(max_length=max_name_length, required=False)
    first_name_4 = forms.CharField(max_length=max_name_length, required=False)
    last_name_4 = forms.CharField(max_length=max_name_length, required=False)
    email = forms.EmailField()

    class Meta:
        fields = ['first_name_0', 'last_name_0',
                  'first_name_1', 'last_name_1',
                  'first_name_2', 'last_name_2',
                  'first_name_3', 'last_name_3',
                  'first_name_4', 'last_name_4',
                  'email']
        labels = {
            'first_name_0': 'First name',
            'last_name_0': 'Last name',
            'first_name_1': 'First name',
            'last_name_1': 'Last name',
            'first_name_2': 'First name',
            'last_name_2': 'Last name',
            'first_name_3': 'First name',
            'last_name_3': 'Last name',
            'first_name_4': 'First name',
            'last_name_4': 'Last name',
            'email': 'Email address'
        }
