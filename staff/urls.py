from django.conf.urls import url

from staff.views import ManageView, HandoverView, EventView, CreateEventView
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
    url(regex=r'^candidate/(?P<candidate_id>[0-9]+)/$',
        view=login_required(HandoverView.as_view()),
        name='handover')
]
