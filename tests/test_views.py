from django.test import Client, TestCase
from register.models import CandidateMetaData
from tests.test_models import CandidateMetaDataTestBase

import re

class ViewTestCase(CandidateMetaDataTestBase):
    def get_match(self, url, params, pattern):
        client = Client()
        response = client.get(url, params)
        self.assertEquals(response.status_code, 200)

        return re.search(pattern, response.content)


class ThanksViewTestCase(ViewTestCase):
    def test_total_number_in_line(self):
        match = self.get_match(url     = '/register/thanks.html',
                               params  = None,
                               pattern = 'total number of (\d+) people')
        self.assertEquals(len(self.test_candidates), int(match.group(1)))


class NumberInLine(ViewTestCase):
    def test_wrong_user_id(self):
        client = Client()
        response = client.get('/register/current-in-line.html')
        self.assertEquals(response.status_code, 400)

    def test_all_user_ids(self):
        for num, candidate in enumerate(CandidateMetaData.objects.all()):
            match = self.get_match(url     = '/register/current-in-line.html',
                                   params  = {'user_id' : candidate.identifier},
                                   pattern = 'Currently you are number (\d+)')
            self.assertEquals(num+1, int(match.group(1)))

