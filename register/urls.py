from django.conf.urls import url

from register.views import ThanksView, ContactView, CurrentInLineView

urlpatterns = [
    url(r'^current-in-line.html', CurrentInLineView.as_view(), name='thanks'),
    url(r'^thanks.html',          ThanksView.as_view(),        name='thanks'),
    url(r'^$',                    ContactView.as_view(),       name='index')
]
