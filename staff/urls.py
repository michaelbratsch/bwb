from django.conf.urls import url

from staff.views import ManageView, HandoverBicycleView, EventView
from staff.views import CreateEventView, CloseEventView
from django.contrib.auth.decorators import login_required

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
    url(regex=r'^close_event/(?P<event_id>[0-9]+)/$',
        view=login_required(CloseEventView.as_view()),
        name='close_event'),
    url(regex=r'^candidate/(?P<candidate_id>[0-9]+)/$',
        view=login_required(HandoverBicycleView.as_view()),
        name='handover')
]
