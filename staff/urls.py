from django.conf.urls import url
from django.contrib.auth.views import logout

from staff.views import LoginView, ManageView, HandoverView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(regex=r'^login/$',
        view=LoginView.as_view(),
        name='login'),
    url(regex=r'^logout/$',
        view=logout,
        name='logout'),
    url(regex=r'^$',
        view=login_required(ManageView.as_view()),
        name='index'),
    url(regex=r'^candidate/(?P<user_id>[0-9]+)/$',
        view=login_required(HandoverView.as_view()),
        name='handover')
]
