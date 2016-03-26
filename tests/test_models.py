from hypothesis.strategies import text, just, builds
from hypothesis.core import given
from hypothesis.extra.django import TestCase as HypothesisTestCase
from hypothesis.extra.django.models import models

from faker import Faker

from register.models import Candidate, Registration, get_hash_value
from register.models import max_name_length


# filter text that only contains of whitespace
name_strategy = text(min_size=1, max_size=max_name_length).filter(lambda x:
                                                                  x.strip())
email_strategy = builds(target=Faker().email)
registration_strategy = models(model=Registration,
                               email_validated=just(False))
candidate_strategy = models(model=Candidate,
                            identifier=builds(get_hash_value),
                            registration=registration_strategy)


class CandidateTestCase(HypothesisTestCase):
    @given(candidate_strategy)
    def test_number_of_candidates(self, candidate):
        self.assertEqual(Candidate.objects.count(), 1)


class RegistrationTestCase(HypothesisTestCase):
    def test_unique_identifiers(self):
        for _ in range(20):
            candidate_strategy.example()

        candidates = Candidate.objects.all()
        identifier_set = set(i.identifier for i in candidates)
        self.assertEqual(len(identifier_set), Candidate.objects.count())
