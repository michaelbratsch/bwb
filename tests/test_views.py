from django.core import mail
from django.core.urlresolvers import reverse

from hypothesis import given, settings, HealthCheck, example
from hypothesis.extra.django import TestCase as HypothesisTestCase
from hypothesis.strategies import random_module

from register.models import Candidate
from tests.test_models import name_strategy, email_strategy, date_strategy,\
    bicycle_kind_strategy, phone_strategy_clean


class ContactViewTestCase(HypothesisTestCase):
    url = reverse('register:registration')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertContains(response=response, text='Register for a bike',
                            count=1)
        self.assertEqual(mail.outbox, [])

    def successful_post(self, post_dict):
        post_dict['agree'] = "True"
        response = self.client.post(self.url, post_dict)

        self.assertRedirects(response, reverse('register:thanks'))

        if 'email' in post_dict:
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to[0], post_dict['email'])

        first_candidate = Candidate.objects.first()
        self.assertEqual(post_dict['first_name'].strip(),
                         first_candidate.first_name)
        self.assertEqual(post_dict['last_name'].strip(),
                         first_candidate.last_name)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(first_name=name_strategy,
           last_name=name_strategy,
           date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           email=email_strategy,
           dummy=random_module())
    @example(first_name='Lore',
             last_name='Seibel',
             date_of_birth='2001-01-12',
             bicycle_kind=2,
             email='asdf@gmx.de')
    def test_email_post(self, **kwargs):
        self.successful_post(kwargs)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(first_name=name_strategy,
           last_name=name_strategy,
           date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           phone_number=phone_strategy_clean,
           dummy=random_module())
    @example(first_name='Bernd',
             last_name='Klaus',
             date_of_birth='2016-02-20',
             bicycle_kind=2,
             phone_number='01631703322')
    @example(first_name='Stefan',
             last_name='Seibert',
             date_of_birth='1977-02-20',
             bicycle_kind=1,
             phone_number='015261703322')
    def test_phone_post(self, **kwargs):
        self.successful_post(kwargs)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(first_name=name_strategy,
           last_name=name_strategy,
           date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           email=email_strategy,
           phone_number=phone_strategy_clean,
           dummy=random_module())
    @example(first_name='Bernd',
             last_name='Klaus',
             date_of_birth='1984-12-20',
             bicycle_kind=3,
             email='gmail@hans.com',
             phone_number='015111316383')
    def test_email_and_phone_post(self, **kwargs):
        self.successful_post(kwargs)

    def check_failed_post(self, field, errors, post_dict, empty_outbox=True):
        response = self.client.post(self.url, post_dict)
        self.assertContains(response=response, text='Register for a bike',
                            count=1)
        self.assertFormError(response=response,
                             form='form',
                             field=field,
                             errors=errors)
        if empty_outbox:
            self.assertEqual(mail.outbox, [])

    number_error = 'This is not a valid number for this region.'
    email_error = 'Enter a valid email address.'
    duplicate_error = ('A user with this name and date of birth is already '
                       'registered. It is not allowed to register multiple '
                       'times!')

    def check_registering_twice(self, post_dict, cases=False):
        self.successful_post(post_dict)

        # ToDo: why does inexact match not work for all unicode characters?
        if cases:
            # check the case-in-sensitive match
            post_dict['first_name'] = post_dict['first_name'].lower()
            post_dict['last_name'] = post_dict['last_name'].upper()

        self.check_failed_post(field='',
                               errors=self.duplicate_error,
                               post_dict=post_dict,
                               empty_outbox=False)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(first_name=name_strategy,
           last_name=name_strategy,
           date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           email=email_strategy,
           dummy=random_module())
    def test_registering_twice_with_email(self, **kwargs):
        self.check_registering_twice(kwargs)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(first_name=name_strategy,
           last_name=name_strategy,
           date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           phone_number=phone_strategy_clean,
           dummy=random_module())
    def test_registering_twice_with_phone(self, **kwargs):
        self.check_registering_twice(kwargs)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(first_name=name_strategy,
           last_name=name_strategy,
           date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           email=email_strategy,
           phone_number=phone_strategy_clean,
           dummy=random_module())
    def test_registering_twice_with_email_and_phone(self, **kwargs):
        self.check_registering_twice(kwargs)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           email=email_strategy,
           phone_number=phone_strategy_clean,
           dummy=random_module())
    def test_registering_twice_case_insensitive(self, **kwargs):
        kwargs['first_name'] = 'Norbert'
        kwargs['last_name'] = 'Franz'
        self.check_registering_twice(kwargs, cases=True)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(first_name=name_strategy,
           last_name=name_strategy,
           date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           dummy=random_module())
    def test_invalid_email_post(self, **kwargs):
        kwargs['email'] = 'asdf'
        self.check_failed_post(field='email',
                               errors=self.email_error,
                               post_dict=kwargs)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(first_name=name_strategy,
           last_name=name_strategy,
           date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           dummy=random_module())
    def test_invalid_phone_post(self, **kwargs):
        kwargs['phone_number'] = '01631'
        self.check_failed_post(field='phone_number',
                               errors=self.number_error,
                               post_dict=kwargs)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(first_name=name_strategy,
           last_name=name_strategy,
           date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           email=email_strategy,
           dummy=random_module())
    def test_valid_email_and_invalid_phone_post(self, **kwargs):
        kwargs['phone_number'] = '88631'
        self.check_failed_post(field='phone_number',
                               errors=self.number_error,
                               post_dict=kwargs)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(first_name=name_strategy,
           last_name=name_strategy,
           date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           phone_number=phone_strategy_clean,
           dummy=random_module())
    def test_invalid_email_and_valid_phone_post(self, **kwargs):
        kwargs['email'] = 'djddj@www'
        self.check_failed_post(field='email',
                               errors=self.email_error,
                               post_dict=kwargs)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(first_name=name_strategy,
           last_name=name_strategy,
           date_of_birth=date_strategy,
           bicycle_kind=bicycle_kind_strategy,
           dummy=random_module())
    def test_invalid_email_and_invalid_phone_post(self, **kwargs):
        kwargs['email'] = 'qwer'
        kwargs['phone_number'] = '88631'
        self.check_failed_post(field='phone_number',
                               errors=self.number_error,
                               post_dict=kwargs)

#########################
#     @given(name=name_strategy, email=email_strategy)
#     def test_failed_name_post(self, name, email):
#         for first_name, last_name in [('', name), (name, '')]:
#             self.check_failed_post({'first_name_0': first_name,
#                                     'last_name_0': last_name,
#                                     'email': email})


# class ThanksViewTestCase(HypothesisTestCase):
#     url = reverse('register:thanks')
#
#     @settings(suppress_health_check=[HealthCheck.too_slow])
#     @given(lists(elements=email_registration_strategy, average_size=3))
#     def test_total_number_in_line(self, candidate):
#         text = 'total number of %s people' % Candidate.objects.count()
#
#         self.assertContains(response=self.client.get(self.url),
#                             text=text, count=1)
#
#
# class CurrentInLineViewTestCase(HypothesisTestCase):
#     url = reverse('register:current-in-line')
#
#     def test_missing_user_id(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 404)
#
#     @given(text())
#     def test_wrong_user_id(self, user_id):
#         response = self.client.get(self.url, {'user_id': user_id})
#         self.assertEqual(response.status_code, 404)
#
#     @settings(suppress_health_check=[HealthCheck.too_slow])
#     @given(lists(elements=email_registration_strategy, average_size=3))
#     def test_all_user_ids(self, list_of_registrations):
#         for registration in User_Registration.objects.all():
#             self.assertFalse(registration.email_validated)
#             for _ in registration.get_candidates():
#                 text = 'Currently you are number %s' % \
#                        registration.number_in_line()
#                 response = self.client.get(self.url,
#                                            {'user_id':
#                                             registration.identifier})
#
#                 self.assertContains(response=response, text=text, count=1)
#
#             self.assertFalse(registration.email_validated)
#             registration.refresh_from_db()
#             self.assertTrue(registration.email_validated)
#
#
# class GreetingsViewTestCase(HypothesisTestCase):
#     url = reverse('index')
#
#     def test_get(self):
#         response = self.client.get(self.url)
#         self.assertContains(response=response, text='I need a bicycle',
#                             count=1)
#
#     def test_failed_post_language_not_found(self):
#         response = self.client.post(self.url, {'language': 'asdf'})
#         self.assertEqual(response.status_code, 400)
#
#     def test_failed_post_missing_key(self):
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 400)
#
#     def test_successfull_post(self):
#         response = self.client.post(self.url, {'language': 'de'})
#         self.assertEqual(response.status_code, 302)
