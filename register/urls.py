from django.conf.urls import url

from register.views import GreetingsView, RegistrationErrorUniquenessView
from register.views import ThanksView, RegistrationView, CurrentInLineView


urlpatterns = [
    url(r'^current-in-line.html',
        CurrentInLineView.as_view(), name='current-in-line'),
    url(r'^thanks.html', ThanksView.as_view(), name='thanks'),
    url(r'^registration.html$', RegistrationView.as_view(),
        name='registration'),
    url(r'^$', GreetingsView.as_view(), name='greeting')
]
