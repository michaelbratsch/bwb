from django.conf.urls import url

from staff.views import ManageView, HandoverView

urlpatterns = [
    url(r'^$', ManageView.as_view(), name='index'),
    url(r'^candidate/(?P<user_id>[0-9]+)/$', HandoverView.as_view(),
        name='handover')
]
