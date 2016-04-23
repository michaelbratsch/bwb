#!/usr/bin/env python

import os

test_email = 'michael.b001@gmx.de'


def populate():

    release_1 = add_release(timezone.now())
    release_2 = add_release(timezone.now()+timedelta(days=1))

    registration_1 = add_registration(release_1, test_email)
    registration_2 = add_registration(release_2, test_email)

    add_candidate(registration_1, 'Stefan', 'Mueller')
    add_candidate(registration_1, 'Simone', 'Peterson')
    add_candidate(registration_1, 'Holger', 'Berens')
    add_candidate(registration_1, 'Andreas', 'Welters')

    add_candidate(registration_2, 'Rolf', 'Brecht')
    add_candidate(registration_2, 'Guenter', 'Brecht')
    add_candidate(registration_2, 'Lothar', 'Brecht')


def add_registration(release, email):
    return Registration.objects.create(release=release, email=email)


def add_candidate(registration, first_name, last_name):
    return Candidate.objects.create(
        registration=registration,
        first_name=first_name,
        last_name=last_name)


def add_release(due_date):
    return Release.objects.create(due_date=due_date)


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
    from register.models import Registration, Candidate, Bicycle, Release
    populate()
