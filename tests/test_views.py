from django.core import mail
from django.core.urlresolvers import reverse

from hypothesis import given, settings, HealthCheck
from hypothesis.extra.django import TestCase as HypothesisTestCase
from hypothesis.strategies import text, lists, random_module

from register.models import Candidate, User_Registration
from tests.test_models import name_strategy, email_strategy, \
    registration_strategy, name_list_strategy


class ContactViewTestCase(HypothesisTestCase):
    url = reverse('register:greeting')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertContains(response=response, text='Register for a bike',
                            count=1)
        self.assertEqual(mail.outbox, [])

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(name_list=name_list_strategy,
           email=email_strategy, dummy=random_module())
    def test_post(self, name_list, email, dummy):
        post_dict = {'email': email}
        for i, name in enumerate(name_list):
            first_name, last_name = name
            post_dict['first_name_%s' % i] = first_name
            post_dict['last_name_%s' % i] = last_name
        response = self.client.post(self.url, post_dict)

        # Http status code 302: URL redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'thanks.html')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], email)

        first_candidate = Candidate.objects.first()
        self.assertEqual(post_dict['first_name_0'].strip(),
                         first_candidate.first_name)
        self.assertEqual(post_dict['last_name_0'].strip(),
                         first_candidate.last_name)

    def check_failed_post(self, post_dict):
        response = self.client.post(self.url, post_dict)
        self.assertContains(response=response, text='Register for a bike',
                            count=1)
        self.assertEqual(mail.outbox, [])

    @given(name_list=name_list_strategy)
    def test_failed_email_post(self, name_list):
        post_dict = {'email': 'asdf'}
        for i, name in enumerate(name_list):
            first_name, last_name = name
            post_dict['first_name_%s' % i] = first_name
            post_dict['last_name_%s' % i] = last_name
        self.check_failed_post(post_dict)

    @given(name=name_strategy, email=email_strategy)
    def test_failed_name_post(self, name, email):
        for first_name, last_name in [('', name), (name, '')]:
            self.check_failed_post({'first_name_0': first_name,
                                    'last_name_0': last_name,
                                    'email': email})


class ThanksViewTestCase(HypothesisTestCase):
    url = reverse('register:thanks')

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(lists(elements=registration_strategy, average_size=3))
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

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(lists(elements=registration_strategy, average_size=3))
    def test_all_user_ids(self, list_of_registrations):
        for registration in User_Registration.objects.all():
            self.assertFalse(registration.email_validated)
            for _ in registration.get_candidates():
                text = 'Currently you are number %s' % \
                       registration.number_in_line()
                response = self.client.get(self.url,
                                           {'user_id':
                                            registration.identifier})

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
