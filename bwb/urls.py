"""bwb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth.views import logout, login
from django.urls import include, re_path, path

from .views import GreetingsView, LegalView

urlpatterns = i18n_patterns(
    re_path(r'^login/$', view=login, kwargs={'template_name': 'login.html'},
            name='login'),
    re_path(r'^logout/$', view=logout, name='logout'),
    re_path(r'^i18n/', include('django.conf.urls.i18n'), name='set_language'),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^register/', include(('register.urls', 'register'))),
    re_path(r'^staff/', include(('staff.urls', 'staff'))),
    re_path(r'^$', GreetingsView.as_view(), name='index'),
    re_path(r'^legal.html$', LegalView.as_view(), name='legal')
)
