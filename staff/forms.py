from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=200)
    password = forms.CharField(max_length=32,
                               widget=forms.PasswordInput)
