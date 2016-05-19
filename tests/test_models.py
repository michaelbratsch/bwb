from faker import Faker
from hypothesis import given, settings, HealthCheck
from hypothesis.extra.django import TestCase as HypothesisTestCase
from hypothesis.extra.django.models import models
from hypothesis.strategies import text, just, builds, lists, sampled_from

from register.models import Candidate, User_Registration, get_hash_value, \
    max_name_length


# filter text that only contains of whitespace
name_strategy = text(min_size=1, max_size=max_name_length).filter(lambda x:
                                                                  x.strip())

bicycle_kind_strategy = sampled_from(
    [value for value, name in User_Registration.BICYCLE_CHOICES])
email_strategy = builds(target=Faker().email)

candidate_strategy = models(model=Candidate,
                            first_name=name_strategy,
                            last_name=name_strategy,
                            date_of_birth=just('2000-10-19'))

# this strategy might take some time and it can be necessary to disable
# the health check for too slow tests
registration_strategy = models(model=User_Registration,
                               candidate=candidate_strategy,
                               bicycle_kind=bicycle_kind_strategy,
                               identifier=builds(get_hash_value),
                               email=email_strategy)


class ModelTestCase(HypothesisTestCase):

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(lists(registration_strategy))
    def test_number_of_candidates(self, list_of_registration):
        """Testing the nested strategy."""
        self.assertEqual(len(list_of_registration), Candidate.total_in_line())

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(lists(registration_strategy))
    def test_unique_identifiers(self, list_of_registrations):
        """Identifiers of registration shall be unique."""
        identifier_set = set(User_Registration.objects.values_list(
            'identifier', flat=True))
        self.assertEqual(
            len(identifier_set), User_Registration.objects.count())
