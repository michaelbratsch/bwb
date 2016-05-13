#!/usr/bin/env python

from datetime import timedelta
from django.utils.dateparse import parse_date
import os
import random

from faker import Faker


test_email = 'michael.b001@gmx.de'

fake = Faker('de')
fake.seed(1)
random.seed(1)


def get_random_date():
    return parse_date('1983-03-31') + timedelta(days=random.randint(-5000,
                                                                    1000))


def populate():
    for _ in range(100):
        candidate = add_candidate(first_name=fake.first_name(),
                                  last_name=fake.last_name(),
                                  date_of_birth=get_random_date())

        add_registration(candidate=candidate,
                         bicycle_kind=random.randint(1, 4),
                         email=fake.email())


def add_candidate(first_name, last_name, date_of_birth):
    return Candidate.objects.create(first_name=first_name,
                                    last_name=last_name,
                                    date_of_birth=date_of_birth)


def add_registration(candidate, bicycle_kind, email):
    return User_Registration.objects.create(candidate=candidate,
                                            bicycle_kind=bicycle_kind,
                                            email=email)


def add_event(due_date):
    return HandoutEvent.objects.create(due_date=due_date)


def add_bicycle():
    b = Bicycle.objects.create()
    return b

# Start execution here!
if __name__ == '__main__':
    print("Starting FIRST_APP population script...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bwb.settings')
    import django
    django.setup()
    from register.models import User_Registration, Candidate, Bicycle
    from register.models import HandoutEvent
    populate()
