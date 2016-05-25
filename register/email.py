from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
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


def send_message_after_registration(registration, request):
    candidate = registration.candidate

    name = "%s %s" % (candidate.first_name, candidate.last_name)
    header = ugettext("Hello %s,") % name

    body = ugettext("Thank you for registering for a bike.\n"
                    "To verify your email address and to check your current "
                    "number in line, please click the following link:")

    page_link = urljoin(reverse('register:current-in-line'),
                        get_url_parameter('user_id', registration.identifier))

    base_url = get_base_url_from_request(request)
    link = urljoin(base_url, page_link)

    footer = ugettext("We hope to see you soon!")
    newline = "\n"

    message = "\n".join((header, newline, body, link, newline, footer))

    if registration.email:
        send_mail(subject=ugettext('BwB - Registration'),
                  message=message,
                  from_email='webmaster@bikeswithoutborders.de',
                  recipient_list=[registration.email],
                  fail_silently=False)

    elif registration.mobile_number:
        message = ugettext("Thank you for registering for a bike.\n"
                           "You will be notified when your bike is ready.\n"
                           "Your BwB Team.")

        smsgate_headers = {'X-SMSGate-User': settings.SMS_GATE_USER,
                           'X-SMSGate-Pwd': settings.SMS_GATE_PASSWORD,
                           'X-SMSGate-Auth-Method': settings.SMS_GATE_AUTH_METHOD,
                           'X-SMSGate-To': registration.mobile_number}

        email = EmailMessage(subject=ugettext('BwB - Registration'),
                             body=message,
                             headers=smsgate_headers,
                             from_email='webmaster@bikeswithoutborders.de',
                             to=['smsgate@bikeswithoutborders.de'])

        email.send(fail_silently=False)

    else:
        assert False, "Messages other than email or sms are currently not supported."
