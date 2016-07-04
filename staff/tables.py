from django.conf import settings
from django.conf.global_settings import SHORT_DATE_FORMAT
from django.core.urlresolvers import reverse_lazy
from django.utils import formats
from django.utils.html import format_html

import django_tables2 as tables
from register.email import get_url_parameter
from register.models import Bicycle, Candidate, HandoutEvent, UserRegistration


def format_date(value):
    return formats.date_format(value,
                               formats.get_format(SHORT_DATE_FORMAT,
                                                  lang=settings.LANGUAGE_CODE))

# pylint: disable=too-few-public-methods
# pylint: disable=no-self-use


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
            for number, display_string in UserRegistration.BICYCLE_CHOICES:
                if number == value:
                    return display_string
            assert False, "Key not found"
        return get_display_value(value)

    def render_bicycle(self, value):
        return value.short_str()

    class Meta(object):
        model = Candidate
        attrs = {'class': 'bootstrap', 'width': '100%'}
        template = 'django_tables2/bootstrap.html'
        empty_text = "There are currently no canditates in the database."
        sequence = ('id', 'status', '...')


class CandidateTable(EventTable):

    class Meta(object):
        model = Candidate
        attrs = {'class': 'bootstrap', 'width': '100%'}
        template = 'django_tables2/bootstrap.html'
        empty_text = "There are currently no canditates in the database."
        sequence = ('id', 'status', '...')


class BicycleTable(tables.Table):

    def render_id(self, value):
        bicycle = Bicycle.objects.get(id=value)
        candidate_id = bicycle.candidate.id
        candidate_url = (reverse_lazy('staff:candidate',
                                      kwargs={'candidate_id': candidate_id}) +
                         get_url_parameter('bicycle_id', value))
        return format_html('<a href="%s">%s</a>' % (candidate_url, value))

    class Meta(object):
        model = Bicycle
        attrs = {'class': 'bootstrap', 'width': '100%'}
        template = 'django_tables2/bootstrap.html'
        empty_text = "There are currently no bicycles in the database."
        sequence = ('id', 'bicycle_number', '...')


class HandoutEventTable(tables.Table):
    invitations = tables.Column(
        verbose_name='Invitations',
        accessor='invitations')
    handed_out = tables.Column(
        verbose_name='Bikes handed out',
        accessor='invitations')

    def render_invitations(self, value):
        return len(value.all())

    def render_handed_out(self, value):
        candidate_status = [
            invitation.candidate.get_status() for invitation in value.all()
        ]
        return candidate_status.count(Candidate.WITH_BICYCLE)

    def render_id(self, value):
        event_url = (reverse_lazy('staff:event', kwargs={'event_id': value}))
        return format_html('<a href="%s">%s</a>' % (event_url, value))

    class Meta(object):
        model = HandoutEvent
        attrs = {'class': 'bootstrap', 'width': '100%'}
        template = 'django_tables2/bootstrap.html'
        empty_text = "There are currently no events in the database."
        sequence = ('id', 'due_date', '...')
