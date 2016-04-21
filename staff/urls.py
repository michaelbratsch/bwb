from django.conf.urls import url

from staff.views import ManageView, HandoverView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(regex=r'^$',
        view=login_required(ManageView.as_view()),
        name='index'),
    url(regex=r'^candidate/(?P<candidate_id>[0-9]+)/$',
        view=login_required(HandoverView.as_view()),
        name='handover')
]
