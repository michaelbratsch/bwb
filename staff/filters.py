from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div
from datetime import datetime, timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import SelectDateWidget
from django_filters import FilterSet, CharFilter
from django_filters.filters import ChoiceFilter, MethodFilter

from register.models import Candidate, Bicycle


EMPTY_CHOICE = ('', '---------'),


class CandidateFilter(FilterSet):
    first_name = CharFilter(lookup_expr='icontains')
    last_name = CharFilter(lookup_expr='icontains')
    status = ChoiceFilter(choices=EMPTY_CHOICE + Candidate.CANDIDATE_STATUS)

    def __init__(self, *args, **kwargs):
        super(CandidateFilter, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'get'

        layout = Div(Div(Field('first_name'),
                         css_class="col-xs-12 col-md-4"),
                     Div(Field('last_name'),
                         css_class="col-xs-12 col-md-4"),
                     Div(Field('status'),
                         css_class="col-xs-12 col-md-4"))

        self.helper.layout = Layout(*layout)

        self.helper.add_input(Submit('submit', 'Filter',
                                     css_class='btn-info'))

    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'status']


class HandoutDateWidget(SelectDateWidget):

    def __init__(self, *args, **kwargs):
        min_year = Bicycle.objects.earliest(
            'date_of_handout').date_of_handout.year
        max_year = Bicycle.objects.latest(
            'date_of_handout').date_of_handout.year
        super(HandoutDateWidget, self).__init__(
            years=range(min_year, max_year + 1)[::-1], *args, **kwargs)


class BicycleForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BicycleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'

        layout = Div(Div(Field('date_of_handout_begin'),
                         css_class="col-xs-12 col-md-6"),
                     Div(Field('date_of_handout_end'),
                         css_class="col-xs-12 col-md-6"))

        self.helper.layout = Layout(*layout)

        self.helper.add_input(Submit('submit', 'Filter',
                                     css_class='btn-info'))

    def clean(self):
        for date_id in ['date_of_handout_begin', 'date_of_handout_end']:
            date_as_str = self.cleaned_data.get(date_id)
            error_message = 'Format of %s is invalid.' % date_id
            if not date_as_str:
                raise ValidationError(error_message)

            try:
                datetime.strptime(date_as_str, '%Y-%m-%d')
            except ValueError:
                raise ValidationError(error_message)


class BicycleFilter(FilterSet):
    date_of_handout_begin = MethodFilter(widget=HandoutDateWidget)
    date_of_handout_end = MethodFilter(widget=HandoutDateWidget)

    class Meta:
        form = BicycleForm
        model = Bicycle
        fields = ['date_of_handout_begin', 'date_of_handout_end']

    # pylint: disable= no-self-use
    def filter_date_of_handout_begin(self, queryset, value):
        return queryset.filter(
            date_of_handout__gt=value)

    def filter_date_of_handout_end(self, queryset, value):
        incr_date = datetime.strptime(value, '%Y-%m-%d') + timedelta(days=1)
        return queryset.filter(
            date_of_handout__lt=incr_date)
