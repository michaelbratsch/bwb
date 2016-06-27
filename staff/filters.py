from datetime import datetime, timedelta
from django.forms.widgets import SelectDateWidget
from django_filters import FilterSet, CharFilter
from django_filters.filters import ChoiceFilter, MethodFilter

from register.models import Candidate, Bicycle


EMPTY_CHOICE = ('', '---------'),


class CandidateFilter(FilterSet):
    first_name = CharFilter(lookup_expr='icontains')
    last_name = CharFilter(lookup_expr='icontains')
    status = ChoiceFilter(choices=EMPTY_CHOICE + Candidate.CANDIDATE_STATUS)

    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'status']


class HandoutDateWidget(SelectDateWidget):

    def __init__(self, *args, **kwargs):
        current_year = datetime.now().year
        super(HandoutDateWidget, self).__init__(
            years=range(2016, current_year + 1)[::-1], *args, **kwargs)


class BicycleFilter(FilterSet):
    begin_date_of_handout = MethodFilter(widget=HandoutDateWidget)
    end_date_of_handout = MethodFilter(widget=HandoutDateWidget)

    class Meta:
        model = Bicycle
        fields = ['begin_date_of_handout', 'end_date_of_handout']

    # pylint: disable= no-self-use
    def filter_begin_date_of_handout(self, queryset, value):
        return queryset.filter(
            date_of_handout__gt=value)

    def filter_end_date_of_handout(self, queryset, value):
        incr_date = datetime.strptime(value, '%Y-%m-%d') + timedelta(days=1)
        return queryset.filter(
            date_of_handout__lt=incr_date)
