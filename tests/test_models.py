from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import text, just, builds, lists
from hypothesis.extra.django import TestCase as HypothesisTestCase
from hypothesis.extra.django.models import models

from faker import Faker

from register.models import Candidate, Registration, get_hash_value, \
    max_name_length

# filter text that only contains of whitespace
name_strategy = text(min_size=1, max_size=max_name_length).filter(lambda x:
                                                                  x.strip())
email_strategy = builds(target=Faker().email)


def generate_with_candidate(registration):
    candidate_strategy = models(model=Candidate,
                                registration=just(registration))
    return lists(elements=candidate_strategy,
                 min_size=1,
                 max_size=5,
                 average_size=2).map(lambda _: registration)

# this strategy might take some time and it can be necessary to disable
# the health check for too slow tests
registration_strategy = models(model=Registration,
                               identifier=builds(get_hash_value),
                               email_validated=just(False)).flatmap(
                                    generate_with_candidate)


class ModelTestCase(HypothesisTestCase):
    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(lists(elements=registration_strategy, average_size=3))
    def test_number_of_candidates(self, list_of_registration):
        total_number_of_candidates = sum(reg.number_of_candidates() for reg in
                                         list_of_registration)
        self.assertEqual(total_number_of_candidates, Candidate.total_in_line())

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(lists(elements=registration_strategy, average_size=3))
    def test_unique_identifiers(self, list_of_registrations):
        registrations = Registration.objects.only('identifier').all()
        identifier_set = set(i.identifier for i in registrations)
        self.assertEqual(len(identifier_set), Registration.objects.count())
