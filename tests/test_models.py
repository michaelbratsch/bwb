from django.test import TestCase
from register.models import Candidate, CandidateMetaData

from itertools import product

class CandidateTestBase(TestCase):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        self.test_candidates = [{'first_name' : 'Stefan', 'last_name' : 'Mueller',
                                 'email' : 'stefan@mueller.net'},
                                {'first_name' : 'Florian', 'last_name' : 'Klaus',
                                 'email' : 'florian.klaus@gmail.com'}]
        n_times = 20
        self.test_candidates = n_times*self.test_candidates


class CandidateTestCase(CandidateTestBase):
    def setUp(self):
        for candidate in self.test_candidates:
            Candidate.objects.create(**candidate)

    def test_number_of_candidates(self):
        self.assertEqual(len(Candidate.objects.all()), len(self.test_candidates))


class CandidateMetaDataTestBase(CandidateTestBase):
    def setUp(self):
        for candidate in self.test_candidates:
            candidate_object = Candidate.objects.create(**candidate)
            candidate_meta_data_object = CandidateMetaData.create(candidate_object)
            candidate_meta_data_object.save()


class CandidateMetaDataTestCase(CandidateMetaDataTestBase):
    def test_number_of_meta_candidates(self):
        self.assertEqual(len(CandidateMetaData.objects.all()),
                         len(self.test_candidates))

    def test_unique_identifiers(self):
        candidate_meta_data_list = list(CandidateMetaData.objects.all())
        identifier_set = set(i.identifier for i in candidate_meta_data_list)
        self.assertEqual(len(identifier_set), len(self.test_candidates))

