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
    release_id = forms.IntegerField(min_value=0)

    class Meta:
        fields = ['email']
        labels = {'email': 'Email address'}
        for i in range(5):
            fields.append('first_name_%s' % i)
            fields.append('last_name_%s' % i)
            labels['first_name_%s' % i] = 'First_name'
            labels['last_name_%s' % i] = 'Last_name'
