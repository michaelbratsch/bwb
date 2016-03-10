from django.core import mail
from django.test import TestCase
from django.core.urlresolvers import reverse

from hypothesis.strategies import text

from register.models import CandidateMetaData
from tests.test_models import CandidateMetaDataTestBase


class ContactViewTestCase(CandidateMetaDataTestBase):
    def __init__(self, *args, **kwargs):
        CandidateMetaDataTestBase.__init__(self, *args, **kwargs)
        self.url = reverse('register:index')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertContains(response=response, text='Register for a bike',
                            count=1)
        self.assertEqual(mail.outbox, [])

    def test_post(self):
        first_name = text(min_size=1, max_size=100).example()
        last_name = text(min_size=1, max_size=100).example()
        email = 'asdf@gmx.de'
        response = self.client.post(self.url,
                                    {'first_name': first_name,
                                     'last_name': last_name,
                                     'email': email})

        # Http status code 302: URL redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'thanks.html')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], email)

    def check_failed_post(self, first_name, last_name, email):
        response = self.client.post(self.url,
                                    {'first_name': first_name,
                                     'last_name': last_name,
                                     'email': email})
        self.assertContains(response=response, text='Register for a bike',
                            count=1)
        self.assertEqual(mail.outbox, [])

    def test_failed_email_post(self):
        first_name = text(min_size=1, max_size=100).example()
        last_name = text(min_size=1, max_size=100).example()
        self.check_failed_post(first_name, last_name, 'asdf')

    def test_failed_name_post(self):
        for first_name, last_name in [('', 'Lorenz'), ('Werner', '')]:
            self.check_failed_post(first_name, last_name, 'asdf@gmx.de')


class ThanksViewTestCase(CandidateMetaDataTestBase):
    def __init__(self, *args, **kwargs):
        CandidateMetaDataTestBase.__init__(self, *args, **kwargs)
        self.url = reverse('register:thanks')

    def test_total_number_in_line(self):
        text = 'total number of %s people' % len(self.test_candidates)

        self.assertContains(response=self.client.get(self.url),
                            text=text, count=1)


class CurrentInLineViewTestCase(CandidateMetaDataTestBase):
    def __init__(self, *args, **kwargs):
        CandidateMetaDataTestBase.__init__(self, *args, **kwargs)
        self.url = reverse('register:current-in-line')

    def test_missing_user_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_wrong_user_id(self):
        response = self.client.get(self.url,
                                   {'user_id': 110})
        self.assertEqual(response.status_code, 404)

    def test_all_user_ids(self):
        for num, candidate in enumerate(CandidateMetaData.objects.all()):
            self.assertFalse(candidate.email_validated)

            text = 'Currently you are number ' + str(num+1)
            response = self.client.get(self.url,
                                       {'user_id': candidate.identifier})

            self.assertContains(response=response, text=text, count=1)

            self.assertFalse(candidate.email_validated)
            candidate.refresh_from_db()
            self.assertTrue(candidate.email_validated)


class GreetingsViewTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        self.url = reverse('index')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertContains(response=response, text='I need a bicycle',
                            count=1)

    def test_failed_post_language_not_found(self):
        response = self.client.post(self.url, {'language': 'asdf'})
        self.assertEqual(response.status_code, 400)

    def test_failed_post_missing_key(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_successfull_post(self):
        response = self.client.post(self.url, {'language': 'de'})
        self.assertEqual(response.status_code, 302)
