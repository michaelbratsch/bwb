from django.conf.urls import url

from register.views import GreetingsView
from register.views import ThanksView, RegistrationView, CurrentInLineView

user_regex = r'^%s/(?P<user_id>\w+)/$'

urlpatterns = [
    url(user_regex % 'current-in-line', CurrentInLineView.as_view(),
        name='current-in-line'),
    url(user_regex % 'thanks', ThanksView.as_view(),
        name='thanks'),
    url(r'^registration.html$', RegistrationView.as_view(),
        name='registration'),
    url(r'^$', GreetingsView.as_view(), name='greeting')
]
