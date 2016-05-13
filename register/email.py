from django.core.mail import send_mail
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


def send_register_email(recipient, base_url):
    header = ugettext("Hello %(name)s,") % recipient
    body = ugettext("Thank you for registering for a bike.\n"
                    "To verify your email address and to check your current "
                    "number in line, please click the following link:")
    page_link = urljoin(reverse('register:current-in-line'),
                        "?" + urlencode({'user_id': recipient['identifier']}))
    link = urljoin(base_url, page_link)
    footer = ugettext("We hope to see you soon!")
    newline = "\n"

    message = "\n".join((header, newline, body, link, newline, footer))

    send_mail(subject=ugettext('BwB - Registration'),
              message=message,
              from_email='webmaster@bikeswithoutborders.de',
              recipient_list=[recipient['email']],
              fail_silently=False)
