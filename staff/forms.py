from django import forms

from register.models import Bicycle


class HandoverForm(forms.ModelForm):
    candidate_id = forms.IntegerField(min_value=0)

    class Meta:
        model = Bicycle
        fields = ['bicycle_number', 'general_remarks', 'candidate_id']

    def __init__(self, *args, **kwargs):
        super(HandoverForm, self).__init__(*args, **kwargs)
        self.fields['general_remarks'].required = False


class EventForm(forms.Form):
    date = forms.DateField()
    time = forms.TimeField()


class CloseEventForm(forms.Form):
    number_of_winners = forms.IntegerField(min_value=0)
    event_id = forms.IntegerField(min_value=0)
