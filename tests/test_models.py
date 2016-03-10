from django.test import TestCase

from hypothesis.strategies import text

from register.models import Candidate, CandidateMetaData


def create_candidates(n_candidates):
    first_name_strat = text(min_size=1, max_size=100)
    last_name_strat = text(min_size=1, max_size=100)
    for _ in range(n_candidates):
        first_name = first_name_strat.example()
        last_name = last_name_strat.example()
        yield {'first_name': first_name,
               'last_name': last_name,
               'email': '%s@%s.de' % (first_name, last_name)}


class CandidateTestBase(TestCase):
    test_candidates = list(create_candidates(20))

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)


class CandidateTestCase(CandidateTestBase):
    def setUp(self):
        for candidate_dict in self.test_candidates:
            Candidate.objects.create(**candidate_dict)

    def test_number_of_candidates(self):
        self.assertEqual(len(Candidate.objects.all()),
                         len(self.test_candidates))


class CandidateMetaDataTestBase(CandidateTestBase):
    def setUp(self):
        for candidate_dict in self.test_candidates:
            candidate = Candidate.objects.create(**candidate_dict)
            CandidateMetaData.objects.create(candidate=candidate)


class CandidateMetaDataTestCase(CandidateMetaDataTestBase):
    def test_number_of_meta_candidates(self):
        self.assertEqual(len(CandidateMetaData.objects.all()),
                         len(self.test_candidates))

    def test_unique_identifiers(self):
        candidate_meta_data_list = list(CandidateMetaData.objects.all())
        identifier_set = set(i.identifier for i in candidate_meta_data_list)
        self.assertEqual(len(identifier_set), len(self.test_candidates))
