from django.core.mail import send_mail

from bwb.settings import BASE_URL


def send_register_email(recipient, name, identifier):
    lines = ("Hello %s,\n" % name,
             "Thank you for registering for a bike.",
             "To verify your email address and to check your current "
             "number in line, please click the following link:",
             "http://%s/register/current-in-line.html?user_id=%s" %
             (BASE_URL, identifier),
             "\nWe hope to see you soon!")

    message = "\n".join(lines)

    send_mail(subject='Bwb - Registration',
              message=message,
              from_email='foobar@gmail.com',
              recipient_list=[recipient],
              fail_silently=False)
