#!/usr/bin/env python

import os

test_email = 'michael.b001@gmx.de'


def populate():

    event_1 = add_event(timezone.now()+timedelta(days=7))
    event_2 = add_event(timezone.now()+timedelta(days=14))
    event_3 = add_event(timezone.now()+timedelta(days=21))

    registration_1 = add_registration(event_1, test_email)
    registration_2 = add_registration(event_2, test_email)
    registration_3 = add_registration(event_3, test_email)

    add_candidate(registration_1, 'Stefan', 'Mueller')
    add_candidate(registration_1, 'Simone', 'Peterson')
    add_candidate(registration_1, 'Holger', 'Berens')
    add_candidate(registration_1, 'Andreas', 'Welters')
    add_candidate(registration_1, 'Linda', 'Mueller')

    add_candidate(registration_2, 'Rolf', 'Brecht')
    add_candidate(registration_2, 'Guenter', 'Brecht')
    add_candidate(registration_2, 'Lothar', 'Brecht')
    add_candidate(registration_2, 'Lisa', 'Schulz')

    add_candidate(registration_3, 'Holger', 'Adams')
    add_candidate(registration_3, 'Steve', 'Adams')
    add_candidate(registration_3, 'Stefan', 'Boehm')


def add_registration(event, email):
    return Registration.objects.create(event=event, email=email)


def add_candidate(registration, first_name, last_name):
    return Candidate.objects.create(
        registration=registration,
        first_name=first_name,
        last_name=last_name)


def add_event(due_date):
    return Event.objects.create(due_date=due_date)


def add_bicycle():
    b = Bicycle.objects.create()
    return b

# Start execution here!
if __name__ == '__main__':
    print "Starting FIRST_APP population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bwb.settings')
    import django
    django.setup()
    from django.utils import timezone
    from datetime import timedelta
    from register.models import Registration, Candidate, Bicycle, Event
    populate()
