from hypothesis.strategies import text, just, builds
from hypothesis.core import given
from hypothesis.extra.django import TestCase as HypothesisTestCase
from hypothesis.extra.django.models import models

from faker import Faker

from register.models import Candidate, Registration, get_hash_value


# filter text that only contains of whitespace
name_strategy = text(min_size=1, max_size=100).filter(lambda x: x.strip())
email_strategy = builds(target=Faker().email)
registration_strategy = models(model=Registration,
                               identifier=builds(get_hash_value),
                               email_validated=just(False))
candidate_strategy = models(model=Candidate,
                            registration=registration_strategy)


class CandidateTestCase(HypothesisTestCase):
    @given(candidate_strategy)
    def test_number_of_candidates(self, candidate):
        self.assertEqual(Candidate.objects.count(), 1)


class RegistrationTestCase(HypothesisTestCase):
    def test_unique_identifiers(self):
        for _ in range(20):
            candidate_strategy.example()

        registrations = Registration.objects.all()
        identifier_set = set(i.identifier for i in registrations)
        self.assertEqual(len(identifier_set), Registration.objects.count())
