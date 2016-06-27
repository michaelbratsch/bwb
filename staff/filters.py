from django.forms.widgets import SelectDateWidget
from django_filters import DateFilter
from django_filters import FilterSet, CharFilter
from django_filters.filters import ChoiceFilter

from register.models import Candidate, Bicycle

EMPTY_CHOICE = ('', '---------'),


class CandidateFilter(FilterSet):
    first_name = CharFilter(lookup_expr='icontains')
    last_name = CharFilter(lookup_expr='icontains')
    status = ChoiceFilter(choices=EMPTY_CHOICE + Candidate.CANDIDATE_STATUS)

    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'status']


class BicycleFilter(FilterSet):
    date_of_handout = DateFilter(widget=SelectDateWidget)

    class Meta:
        model = Bicycle
        fields = ['date_of_handout']
