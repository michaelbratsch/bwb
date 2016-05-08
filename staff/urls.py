from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from staff.views import CandidateView, EventView, ManageView
from staff.views import CreateEventView, InviteView, ModifyCandidateView
from staff.views import HandoverBicycleView, CandidateOverviewView


urlpatterns = [
    url(regex=r'^$',
        view=login_required(ManageView.as_view()),
        name='index'),
    url(regex=r'^event/(?P<event_id>[0-9]+)/$',
        view=login_required(EventView.as_view()),
        name='event'),
    url(regex=r'^create_event/$',
        view=login_required(CreateEventView.as_view()),
        name='create_event'),
    url(regex=r'^invite/(?P<event_id>[0-9]+)/$',
        view=login_required(InviteView.as_view()),
        name='invite'),
    url(regex=r'^candidate_overview/$',
        view=login_required(CandidateOverviewView.as_view()),
        name='candidate_overview'),
    url(regex=r'^candidate/(?P<candidate_id>[0-9]+)/$',
        view=login_required(CandidateView.as_view()),
        name='candidate'),
    url(regex=r'^modify_candidate/(?P<candidate_id>[0-9]+)/$',
        view=login_required(ModifyCandidateView.as_view()),
        name='modify_candidate'),
    url(regex=r'^handover_bicycle/(?P<candidate_id>[0-9]+)/$',
        view=login_required(HandoverBicycleView.as_view()),
        name='handover_bicycle')
]
