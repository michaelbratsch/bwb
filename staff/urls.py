from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from register.models import Candidate

from staff.views import BicycleOverviewView, CreateCandidateView,\
    DeleteCandidateView
from staff.views import CandidateView, EventView, ManageView, EventOverviewView
from staff.views import CreateEventView, AutoInviteView, ModifyCandidateView
from staff.views import HandoverBicycleView, CandidateOverviewView
from staff.views import RefundBicycleView, InviteCandidateView


EVENT_PATTERN = r'^%s/(?P<event_id>[0-9]+)/$'
CANDIDATE_PATTERN = r'^%s/(?P<candidate_id>[0-9]+)/$'
BICYCLE_PATTERN = r'^%s/(?P<bicycle_id>[0-9]+)/$'

urlpatterns = [
    url(regex=r'^$',
        view=login_required(ManageView.as_view()),
        name='index'),

    # URLs related to bicycles
    url(regex=r'^bicycle_overview.html$',
        view=login_required(BicycleOverviewView.as_view()),
        name='bicycle_overview'),

    # URLs related to events
    url(regex=r'^event_overview.html$',
        view=login_required(EventOverviewView.as_view()),
        name='event_overview'),
    url(regex=EVENT_PATTERN % 'event',
        view=login_required(EventView.as_view()),
        name='event'),
    url(regex=EVENT_PATTERN % 'invite',
        view=login_required(AutoInviteView.as_view()),
        name='invite'),
    url(regex=r'^create_event/$',
        view=login_required(CreateEventView.as_view()),
        name='create_event'),

    # URLs related to candidates
    url(regex=r'^candidate_overview.html$',
        view=login_required(CandidateOverviewView.as_view(
            query_set=Candidate.objects.all())),
        name='candidate_overview'),
    url(regex=r'^create_candidate.html$',
        view=login_required(CreateCandidateView.as_view()),
        name='create_candidate'),


    url(regex=CANDIDATE_PATTERN % 'candidate',
        view=login_required(CandidateView.as_view()),
        name='candidate'),
    url(regex=CANDIDATE_PATTERN % 'modify_candidate',
        view=login_required(ModifyCandidateView.as_view()),
        name='modify_candidate'),
    url(regex=CANDIDATE_PATTERN % 'handover_bicycle',
        view=login_required(HandoverBicycleView.as_view()),
        name='handover_bicycle'),
    url(regex=CANDIDATE_PATTERN % 'refund_bicycle',
        view=login_required(RefundBicycleView.as_view()),
        name='refund_bicycle'),
    url(regex=CANDIDATE_PATTERN % 'invite_candidate',
        view=login_required(InviteCandidateView.as_view()),
        name='invite_candidate'),
    url(regex=CANDIDATE_PATTERN % 'delete_candidate',
        view=login_required(DeleteCandidateView.as_view()),
        name='delete_candidate')
]
