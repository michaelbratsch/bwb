from django import forms

from register.models import max_name_length, User_Registration, Candidate


class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=max_name_length, required=True)
    last_name = forms.CharField(max_length=max_name_length, required=True)
    date_of_birth = forms.DateField(required=True)

    email = forms.EmailField(required=True)
    bicycle_kind = forms.ChoiceField(
        choices=User_Registration.BICYCLE_CHOICES,
        required=True)

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        try:
            first_name = cleaned_data['first_name']
            last_name = cleaned_data['last_name']
            date_of_birth = cleaned_data['date_of_birth']
        except KeyError:
            pass
        except:
            raise
        else:
            if Candidate.get_matching(first_name=first_name,
                                      last_name=last_name,
                                      date_of_birth=date_of_birth):
                raise forms.ValidationError("A candidate with this identity "
                                            "information already exists.")
