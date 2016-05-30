from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django import forms
from django.shortcuts import get_object_or_404

from django.utils.formats import date_format

from register.models import Bicycle, Candidate


class CreateCandidateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'date_of_birth']


def get_hidden_field(name, var):
    def trunk(var):
        if var:
            return var
        return ""

    return [Field(name, type='hidden', value=trunk(var))]


def get_hidden_fields(candidate_id, event_id, bicycle_id):
    return (get_hidden_field('candidate_id', candidate_id) +
            get_hidden_field('event_id', event_id) +
            get_hidden_field('bicycle_id', bicycle_id))


class DeleteCandidateForm(forms.Form):
    event_id = forms.IntegerField(min_value=0, required=False)
    bicycle_id = forms.IntegerField(min_value=0, required=False)
    candidate_id = forms.IntegerField(min_value=0)

    def __init__(self, candidate_id=None, event_id=None, bicycle_id=None,
                 *args, **kwargs):
        super(DeleteCandidateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(*get_hidden_fields(
            candidate_id, event_id, bicycle_id))
        self.helper.add_input(Submit('submit', 'Delete Candidate',
                                     css_class='col-xs-3 btn-info'))


class InviteCandidateForm(forms.Form):
    event_id = forms.IntegerField(min_value=0, required=False)
    candidate_id = forms.IntegerField(min_value=0)
    invitation_event_id = forms.IntegerField(min_value=0)

    def __init__(self, candidate_id=None, event_id=None, bicycle_id=None,
                 *args, **kwargs):
        super(InviteCandidateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        if candidate_id:
            candidate = get_object_or_404(Candidate, id=candidate_id)

            event_choices = [(event.id, date_format(event.due_date,
                                                    'DATETIME_FORMAT'))
                             for event in candidate.events_not_invited_to]

            self.fields['invitation_event_id'] = forms.ChoiceField(
                choices=event_choices)

            layout = [Field('invitation_event_id', required='')]
            layout += get_hidden_field('candidate_id', candidate_id)
            layout += get_hidden_field('event_id', event_id)

            self.helper.layout = Layout(*layout)

            self.helper.form_show_labels = False
            self.helper.add_input(Submit('submit', 'Submit',
                                         css_class='col-xs-3 btn-info'))


class ModifyCandidateForm(forms.ModelForm):
    event_id = forms.IntegerField(min_value=0, required=False)
    bicycle_id = forms.IntegerField(min_value=0, required=False)
    candidate_id = forms.IntegerField(min_value=0)

    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'date_of_birth',
                  'event_id', 'bicycle_id', 'candidate_id']

    def __init__(self, candidate_id=None, event_id=None, bicycle_id=None,
                 *args, **kwargs):
        super(ModifyCandidateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        if candidate_id:
            candidate = get_object_or_404(Candidate, id=candidate_id)

            # ToDo: replace following hack and find out why date_format is
            # not working properly with i10n
            from django.template import Template, Context
            c = Context(dict(candidate=candidate))
            date_of_birth = Template(
                "{{ candidate.date_of_birth|date:'SHORT_DATE_FORMAT' }}"
            ).render(c)

            layout = [Field('first_name', required='',
                            value=candidate.first_name),
                      Field('last_name', required='',
                            value=candidate.last_name),
                      Field('date_of_birth', required='',
                            id='datepicker', value=date_of_birth)]

            layout += get_hidden_fields(candidate_id, event_id, bicycle_id)

            self.helper.layout = Layout(*layout)

            self.helper.add_input(Submit('submit', 'Submit',
                                         css_class='col-xs-3 btn-info'))


class RefundForm(forms.Form):
    event_id = forms.IntegerField(min_value=0, required=False)
    bicycle_id = forms.IntegerField(min_value=0, required=False)
    candidate_id = forms.IntegerField(min_value=0)

    def __init__(self, candidate_id=None, event_id=None, bicycle_id=None,
                 *args, **kwargs):
        super(RefundForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(*get_hidden_fields(
            candidate_id, event_id, bicycle_id))
        self.helper.add_input(Submit('submit', 'Refund bicycle',
                                     css_class='col-xs-3 btn-info'))


class HandoverForm(forms.ModelForm):
    event_id = forms.IntegerField(min_value=0, required=False)
    bicycle_id = forms.IntegerField(min_value=0, required=False)
    candidate_id = forms.IntegerField(min_value=0)

    class Meta:
        model = Bicycle
        fields = ['bicycle_number', 'general_remarks', 'lock_combination',
                  'color', 'brand', 'event_id', 'candidate_id', 'bicycle_id']

    def __init__(self, candidate_id=None, event_id=None, bicycle_id=None,
                 *args, **kwargs):
        super(HandoverForm, self).__init__(*args, **kwargs)
        self.fields['general_remarks'].required = False

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        layout = [Field('bicycle_number', required=''),
                  Field('lock_combination', required=''),
                  Field('color', required=''),
                  Field('brand', required='')]
        layout += get_hidden_fields(candidate_id, event_id, bicycle_id)
        layout += ['general_remarks']

        self.helper.layout = Layout(*layout)

        self.helper.add_input(Submit('submit', 'Submit',
                                     css_class='col-xs-3 btn-info'))


class EventForm(forms.Form):
    due_date = forms.DateTimeField(input_formats=['%d.%m.%Y %H:%M',
                                                  '%m/%d/%Y %I:%M %p'])


class InviteForm(forms.Form):
    event_id = forms.IntegerField(min_value=0)

    choice_1 = forms.IntegerField(min_value=0)
    choice_2 = forms.IntegerField(min_value=0)
    choice_3 = forms.IntegerField(min_value=0)
    choice_4 = forms.IntegerField(min_value=0)
