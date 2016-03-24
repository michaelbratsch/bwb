from django.core import mail
from django.core.urlresolvers import reverse

from hypothesis import given
from hypothesis.strategies import text, random_module
from hypothesis.extra.django import TestCase as HypothesisTestCase

from register.models import Registration, Candidate
from tests.test_models import name_strategy, email_strategy, candidate_strategy


class ContactViewTestCase(HypothesisTestCase):
    url = reverse('register:index')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertContains(response=response, text='Register for a bike',
                            count=1)
        self.assertEqual(mail.outbox, [])

    @given(first_name=name_strategy, last_name=name_strategy,
           email=email_strategy, dummy=random_module())
    def test_post(self, first_name, last_name, email, dummy):
        response = self.client.post(self.url,
                                    {'first_name': first_name,
                                     'last_name': last_name,
                                     'email': email})

        # Http status code 302: URL redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'thanks.html')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], email)

        last_candidate = Candidate.objects.last()
        self.assertEqual(first_name.strip(), last_candidate.first_name)
        self.assertEqual(last_name.strip(), last_candidate.last_name)

    def check_failed_post(self, first_name, last_name, email):
        response = self.client.post(self.url,
                                    {'first_name': first_name,
                                     'last_name': last_name,
                                     'email': email})
        self.assertContains(response=response, text='Register for a bike',
                            count=1)
        self.assertEqual(mail.outbox, [])

    @given(first_name=name_strategy, last_name=name_strategy)
    def test_failed_email_post(self, first_name, last_name):
        self.check_failed_post(first_name, last_name, 'asdf')

    @given(name=name_strategy, email=email_strategy)
    def test_failed_name_post(self, name, email):
        for first_name, last_name in [('', name), (name, '')]:
            self.check_failed_post(first_name, last_name, email)


class ThanksViewTestCase(HypothesisTestCase):
    url = reverse('register:thanks')

    @given(candidate_strategy)
    def test_total_number_in_line(self, candidate):
        text = 'total number of %s people' % Candidate.objects.count()

        self.assertContains(response=self.client.get(self.url),
                            text=text, count=1)


class CurrentInLineViewTestCase(HypothesisTestCase):
    url = reverse('register:current-in-line')

    def test_missing_user_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    @given(text())
    def test_wrong_user_id(self, user_id):
        response = self.client.get(self.url, {'user_id': user_id})
        self.assertEqual(response.status_code, 404)

    def test_all_user_ids(self):
        for _ in range(20):
            candidate_strategy.example()

        for num, registration in enumerate(Registration.objects.all()):
            self.assertFalse(registration.email_validated)

            text = 'Currently you are number ' + str(num+1)
            response = self.client.get(self.url,
                                       {'user_id': registration.identifier})

            self.assertContains(response=response, text=text, count=1)

            self.assertFalse(registration.email_validated)
            registration.refresh_from_db()
            self.assertTrue(registration.email_validated)


class GreetingsViewTestCase(HypothesisTestCase):
    url = reverse('index')

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
