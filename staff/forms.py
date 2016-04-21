from django import forms

from register.models import Bicycle


class HandoverForm(forms.ModelForm):
    class Meta:
        model = Bicycle
        fields = ['bicycle_number', 'general_remarks']
