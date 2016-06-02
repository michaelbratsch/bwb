from django.conf.global_settings import DATETIME_FORMAT
from django.core.urlresolvers import reverse
from django.utils import translation, formats

from django.core.mail import send_mail
from django.utils.translation import ugettext


# To support Python 2 and 3
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


def get_base_url_from_request(request):
    return '{scheme}://{host}'.format(scheme=request.scheme,
                                      host=request.get_host())


def get_url_parameter(name, value):
    if value:
        return "?" + urlencode({name: value})
    return ""


def send_message(registration, subject, message):

    if registration.email:
        send_mail(subject=subject,
                  message=message,
                  from_email='webmaster@bikeswithoutborders.de',
                  recipient_list=[registration.email],
                  fail_silently=False)


def send_message_after_invitation(candidate, handout_event):
    registration = candidate.user_registration

    if registration:
        with translation.override(registration.language):
            name = "%s %s" % (candidate.first_name, candidate.last_name)
            header = "%s %s," % (ugettext("Hello"), name)

            body = (
                ugettext("We have a ") +
                registration.get_bicycle_kind_display() +
                ugettext(" that is reserved for you. Please come by on ") +
                formats.date_format(handout_event.due_date, DATETIME_FORMAT) +
                ugettext(", so that we can fix it together with your help."))

            newline = "\n"
            footer = ugettext("Your,") + newline + ugettext('BwB-Team')

            message = newline.join((header, newline, body, newline, footer))

            subject = ugettext('BwB - Get your bike')

        send_message(registration, subject, message)


def send_message_after_registration(registration, request):
    candidate = registration.candidate

    name = "%s %s" % (candidate.first_name, candidate.last_name)
    header = "%s %s," % (ugettext("Hello"), name)

    body = (ugettext("Thank you for registering for a bike.") + "\n" +
            ugettext("To verify your email address and to check your current "
                     "number in line, please click the following link:"))

    page_link = reverse('register:current-in-line',
                        kwargs={'user_id': registration.identifier})

    base_url = get_base_url_from_request(request)
    link = urljoin(base_url, page_link)

    footer = ugettext("We hope to see you soon!")
    newline = "\n"

    message = newline.join((header, newline, body, link, newline, footer))
    subject = ugettext('BwB - Registration')

    send_message(registration, subject, message)
