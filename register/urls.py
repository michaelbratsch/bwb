from django.conf.urls import url

from register.views import GreetingsView
from register.views import ThanksView, RegistrationView, CurrentInLineView

USER_REGEX = r'^%s/(?P<user_id>\w+)/$'

urlpatterns = [
    url(USER_REGEX % 'current-in-line', CurrentInLineView.as_view(),
        name='current-in-line'),
    url(USER_REGEX % 'thanks', ThanksView.as_view(),
        name='thanks'),
    url(r'^registration.html$', RegistrationView.as_view(),
        name='registration'),
    url(r'^$', GreetingsView.as_view(), name='greeting')
]
