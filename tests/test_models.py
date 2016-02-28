from django.test import TestCase
from register.models import Candidate, CandidateMetaData

from itertools import product

my_test_candidates = [
    {'first_name' : 'Stefan', 'last_name' : 'Mueller',
     'email' : 'stefan@mueller.net'},
    {'first_name' : 'Florian', 'last_name' : 'Klaus',
     'email' : 'florian.klaus@gmail.com'}]

n_times = 50

class CandidateTestCase(TestCase):
    def setUp(self):
        for candidate, _ in product(my_test_candidates, range(n_times)):
            Candidate.objects.create(**candidate)

    def test_number_of_candidates(self):
        self.assertEqual(len(Candidate.objects.all()),
                         len(my_test_candidates)*n_times)

class CandidateMetaDataTestCase(TestCase):
    def setUp(self):
        for candidate, _ in product(my_test_candidates, range(n_times)):
            candidate_object = Candidate.objects.create(**candidate)
            candidate_meta_data_object = CandidateMetaData.create(candidate_object)
            candidate_meta_data_object.save()

    def test_number_of_meta_candidates(self):
        self.assertEqual(len(CandidateMetaData.objects.all()),
                         len(my_test_candidates)*n_times)

    def test_unique_identifiers(self):
        candidate_meta_data_list = list(CandidateMetaData.objects.all())
        identifier_set = set(i.identifier for i in candidate_meta_data_list)
        self.assertEqual(len(identifier_set),
                         len(my_test_candidates)*n_times)

