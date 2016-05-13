from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from staff.views import BicycleOverviewView, BicycleView
from staff.views import CandidateView, EventView, ManageView, EventOverviewView
from staff.views import CreateCandidateView
from staff.views import CreateEventView, AutoInviteView, ModifyCandidateView
from staff.views import HandoverBicycleView, CandidateOverviewView
from staff.views import RefundBicycleView, InviteCandidateView


event_pattern = r'^%s/(?P<event_id>[0-9]+)/$'
candidate_pattern = r'^%s/(?P<candidate_id>[0-9]+)/$'
bicycle_pattern = r'^%s/(?P<bicycle_id>[0-9]+)/$'

urlpatterns = [
    url(regex=r'^$',
        view=login_required(ManageView.as_view()),
        name='index'),
    # URLs related to events
    url(regex=r'^event_overview/$',
        view=login_required(EventOverviewView.as_view()),
        name='event_overview'),
    url(regex=event_pattern % 'event',
        view=login_required(EventView.as_view()),
        name='event'),
    url(regex=event_pattern % 'invite',
        view=login_required(AutoInviteView.as_view()),
        name='invite'),
    url(regex=r'^create_event/$',
        view=login_required(CreateEventView.as_view()),
        name='create_event'),

    # URLs related to bicycles
    url(regex=r'^bicycle_overview/$',
        view=login_required(BicycleOverviewView.as_view()),
        name='bicycle_overview'),
    url(regex=bicycle_pattern % 'bicycle',
        view=login_required(BicycleView.as_view()),
        name='bicycle'),

    # URLs related to candidates
    url(regex=r'^candidate_overview/$',
        view=login_required(CandidateOverviewView.as_view()),
        name='candidate_overview'),
    url(regex=candidate_pattern % 'candidate',
        view=login_required(CandidateView.as_view()),
        name='candidate'),
    url(regex=candidate_pattern % 'modify_candidate',
        view=login_required(ModifyCandidateView.as_view()),
        name='modify_candidate'),
    url(regex=candidate_pattern % 'handover_bicycle',
        view=login_required(HandoverBicycleView.as_view()),
        name='handover_bicycle'),
    url(regex=candidate_pattern % 'refund_bicycle',
        view=login_required(RefundBicycleView.as_view()),
        name='refund_bicycle'),
    url(regex=candidate_pattern % 'invite_candidate',
        view=login_required(InviteCandidateView.as_view()),
        name='invite_candidate'),
    url(regex=r'^create_candidate/$',
        view=login_required(CreateCandidateView.as_view()),
        name='create_candidate')
]
