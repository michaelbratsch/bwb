from django.conf.urls import url

from register.views import ThanksView, ContactView, CurrentInLineView

urlpatterns = [
    url(r'^current-in-line.html',
        CurrentInLineView.as_view(), name='current-in-line'),
    url(r'^thanks.html', ThanksView.as_view(), name='thanks'),
    url(r'^event/(?P<event_id>[0-9]+)/$', ContactView.as_view(),
        name='index')
]
