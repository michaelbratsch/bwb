"""
WSGI config for bwb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application
import os


os.environ['DJANGO_SETTINGS_MODULE'] = 'bwb.settings_prod'

application = get_wsgi_application()  # pylint: disable=invalid-name
