from django import forms

from register.models import Bicycle, Candidate


class InviteCandidateForm(forms.Form):
    event_id = forms.IntegerField(min_value=0, required=False)
    candidate_id = forms.IntegerField(min_value=0)
    invitation_event_id = forms.IntegerField(min_value=0, required=False)


class CreateCandidateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'date_of_birth']


class ModifyCandidateForm(forms.ModelForm):
    event_id = forms.IntegerField(min_value=0, required=False)
    candidate_id = forms.IntegerField(min_value=0)

    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'date_of_birth',
                  'event_id', 'candidate_id']


class RefundForm(forms.Form):
    event_id = forms.IntegerField(min_value=0, required=False)
    candidate_id = forms.IntegerField(min_value=0)


class HandoverForm(forms.ModelForm):
    event_id = forms.IntegerField(min_value=0, required=False)
    candidate_id = forms.IntegerField(min_value=0)

    class Meta:
        model = Bicycle
        fields = ['bicycle_number', 'general_remarks', 'lock_combination',
                  'event_id', 'candidate_id', 'color', 'brand']

    def __init__(self, *args, **kwargs):
        super(HandoverForm, self).__init__(*args, **kwargs)
        self.fields['general_remarks'].required = False


class EventForm(forms.Form):
    due_date = forms.DateTimeField(input_formats=['%d.%m.%Y %H:%M',
                                                  '%m/%d/%Y %I:%M %p'])


class InviteForm(forms.Form):
    event_id = forms.IntegerField(min_value=0)

    choice_1 = forms.IntegerField(min_value=0)
    choice_2 = forms.IntegerField(min_value=0)
    choice_3 = forms.IntegerField(min_value=0)
    choice_4 = forms.IntegerField(min_value=0)
