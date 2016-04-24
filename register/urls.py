from django.conf.urls import url

from register.views import ThanksView, RegistrationView, CurrentInLineView
from register.views import GreetingsView

urlpatterns = [
    url(r'^current-in-line.html',
        CurrentInLineView.as_view(), name='current-in-line'),
    url(r'^thanks.html', ThanksView.as_view(), name='thanks'),
    url(r'^event/(?P<event_id>[0-9]+)/$', RegistrationView.as_view(),
        name='registration'),
    url(r'^$', GreetingsView.as_view(), name='greeting')
]
