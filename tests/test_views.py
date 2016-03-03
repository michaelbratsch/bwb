from django.core import mail

from hypothesis.strategies import text
import re

from register.models import CandidateMetaData
from tests.test_models import CandidateMetaDataTestBase


class ViewTestCase(CandidateMetaDataTestBase):
    def get_match(self, pattern, params=None, action=None):
        if action is None:
            action = self.client.get
        response = action(self.url, params)
        self.assertEqual(response.status_code, 200)

        match = re.search(pattern, str(response.content))
        self.assertTrue(match)
        return match


class ContactViewTestCase(ViewTestCase):
    def __init__(self, *args, **kwargs):
        ViewTestCase.__init__(self, *args, **kwargs)
        self.url = '/register/'

    def test_get(self):
        self.get_match(pattern = 'Register for a bike')
        self.assertEqual(mail.outbox, [])

    def test_post(self):
        first_name = text(min_size=1, max_size=100).example()
        last_name = text(min_size=1, max_size=100).example()
        email = 'asdf@gmx.de'
        response = self.client.post(self.url,
                                    {'first_name' : first_name,
                                     'last_name'  : last_name,
                                     'email'      : email})
        # Http status code 302: URL redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'thanks.html')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], email)

    def test_failed_email_post(self):
        first_name = text(min_size=1, max_size=100).example()
        last_name = text(min_size=1, max_size=100).example()
        self.get_match(pattern = 'Register for a bike',
                       params  = {'first_name' : first_name,
                                  'last_name'  : last_name,
                                  'email'      : 'asdf'},
                       action  = self.client.post)

        self.assertEqual(mail.outbox, [])

    def test_failed_name_post(self):
        for first_name, last_name in [('', 'Lorenz'), ('Werner', '')]:
            self.get_match(pattern = 'Register for a bike',
                           params  = {'first_name' : first_name,
                                      'last_name'  : last_name,
                                      'email'      : 'asdf@gmx.de'},
                           action  = self.client.post)

            self.assertEqual(mail.outbox, [])


class ThanksViewTestCase(ViewTestCase):
    def __init__(self, *args, **kwargs):
        ViewTestCase.__init__(self, *args, **kwargs)
        self.url = '/register/thanks.html'

    def test_total_number_in_line(self):
        match = self.get_match(pattern = 'total number of (\d+) people')
        self.assertEqual(len(self.test_candidates), int(match.group(1)))


class CurrentInLineViewTestCase(ViewTestCase):
    def __init__(self, *args, **kwargs):
        ViewTestCase.__init__(self, *args, **kwargs)
        self.url = '/register/current-in-line.html'

    def test_wrong_user_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_all_user_ids(self):
        for num, candidate in enumerate(CandidateMetaData.objects.all()):
            self.assertFalse(candidate.email_validated)
            match = self.get_match(params  = {'user_id' : candidate.identifier},
                                   pattern = 'Currently you are number (\d+)')
            self.assertEqual(num+1, int(match.group(1)))

            self.assertFalse(candidate.email_validated)
            candidate.refresh_from_db()
            self.assertTrue(candidate.email_validated)

