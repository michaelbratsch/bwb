from django.conf import settings
from django.conf.global_settings import SHORT_DATE_FORMAT
from django.core.urlresolvers import reverse_lazy
from django.utils import formats
from django.utils.html import format_html

from register.email import get_url_parameter
from register.models import Bicycle, Candidate, User_Registration
import django_tables2 as tables


def format_date(value):
    return formats.date_format(value,
                               formats.get_format(SHORT_DATE_FORMAT,
                                                  lang=settings.LANGUAGE_CODE))


class EventTable(tables.Table):
    first_name = tables.Column(verbose_name='First Name')
    last_name = tables.Column(verbose_name='Last Name')
    date_of_birth = tables.Column(verbose_name='Date of Birth')
    invitations = tables.Column(
        verbose_name='Invitations',
        accessor='invitations')
    wanted_bicycle = tables.Column(
        verbose_name='Wanted bicycle',
        accessor='user_registration.bicycle_kind')
    bicycle = tables.Column(
        verbose_name='Bicycle',
        accessor='bicycle',
        order_by='bicycle.bicycle_number')

    def __init__(self, data, event_id=None, *args, **kwargs):
        super(EventTable, self).__init__(data, *args, **kwargs)
        self.event_id = event_id

    def render_id(self, value):
        candidate_url = (reverse_lazy('staff:candidate',
                                      kwargs={'candidate_id': value}) +
                         get_url_parameter('event_id', self.event_id))
        return format_html('<a href="%s">%s</a>' % (candidate_url, value))

    def render_date_of_birth(self, value):
        return format_date(value)

    def render_invitations(self, value):
        date_of_handout = [format_date(i.handout_event.due_date.date())
                           for i in value.all()]
        return format_html("<br>".join(date_of_handout))

    def render_wanted_bicycle(self, value):
        def get_display_value(value):
            for v, n in User_Registration.BICYCLE_CHOICES:
                if v == value:
                    return n
            assert False, "Key not found"
        return get_display_value(value)

    def render_bicycle(self, value):
        return value.short_str()

    class Meta:
        model = Candidate
        attrs = {'class': 'bootstrap', 'width': '1000%'}
        template = 'django_tables2/bootstrap.html'
        empty_text = "There are currently no canditates in the database."


class CandidateTable(EventTable):

    current_status = tables.Column(
        verbose_name='Status',
        accessor='get_status',
        orderable=False)

    class Meta:
        model = Candidate
        attrs = {'class': 'bootstrap', 'width': '1000%'}
        template = 'django_tables2/bootstrap.html'
        empty_text = "There are currently no canditates in the database."
        sequence = ('current_status', '...')


class BicycleTable(tables.Table):

    def render_id(self, value):
        bicycle = Bicycle.objects.get(id=value)
        candidate_id = bicycle.candidate.id
        candidate_url = (reverse_lazy('staff:candidate',
                                      kwargs={'candidate_id': candidate_id}) +
                         get_url_parameter('bicycle_id', value))
        return format_html('<a href="%s">%s</a>' % (candidate_url, value))

    class Meta:
        model = Bicycle
        attrs = {'class': 'bootstrap', 'width': '100%'}
        template = 'django_tables2/bootstrap.html'
        empty_text = "There are currently no bicycles in the database."
        sequence = ('id', 'bicycle_number', '...')
