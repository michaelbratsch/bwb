import phonenumbers

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from faker import Faker
from hypothesis import given, settings, HealthCheck
from hypothesis.extra.django import TestCase as HypothesisTestCase
from hypothesis.extra.django.models import models
from hypothesis.strategies import integers, random_module
from hypothesis.strategies import just, text, builds, lists, sampled_from

from register.forms import parse_phone_number, mobile_phone_prefixes
from register.models import Candidate, User_Registration, max_name_length


# filter text that only contains of whitespace
name_strategy = text(min_size=1, max_size=max_name_length).filter(lambda x:
                                                                  x.strip())
date_strategy = builds(target=Faker('de').date)

bicycle_kind_strategy = sampled_from(
    [value for value, name in User_Registration.BICYCLE_CHOICES])


def create_email_address():
    while True:
        # filter out the email addresses from Faker that are not valid
        email = Faker('de').email()
        try:
            validate_email(email)
        except ValidationError:
            pass
        else:
            return email

email_strategy = builds(target=create_email_address)


def create_phone_number():
    prefix_strat = sampled_from(mobile_phone_prefixes)
    number_strat = integers(min_value=500000, max_value=999999999)
    while True:
        prefix = prefix_strat.example()
        number = number_strat.example()
        phone_number = '%s%s' % (prefix, number)

        try:
            return parse_phone_number(phone_number)
        except ValidationError:
            pass


# this is just a verifier
def valid_phone_number(number):
    parsed_number = phonenumbers.parse(number, 'DE')

    assert phonenumbers.is_valid_number_for_region(
        parsed_number, 'de'), parsed_number
    return True

phone_strategy = builds(target=create_phone_number)
phone_strategy_clean = phone_strategy.filter(lambda x:
                                             valid_phone_number(x))

candidate_dict = {'model': Candidate,
                  'first_name': name_strategy,
                  'last_name': name_strategy,
                  'date_of_birth': date_strategy}

candidate = models(**candidate_dict)


def generate_email_registration(candidate):
    return models(model=User_Registration,
                  email=email_strategy,
                  candidate=just(candidate))

candidate_with_email = models(**candidate_dict).flatmap(
    generate_email_registration)


def generate_phone_registration(candidate):
    return models(model=User_Registration,
                  phone_number=phone_strategy_clean,
                  candidate=just(candidate))

candidate_with_phone = models(**candidate_dict).flatmap(
    generate_phone_registration)


def generate_email_and_phone_registration(candidate):
    return models(model=User_Registration,
                  email=email_strategy,
                  phone_number=phone_strategy_clean,
                  candidate=just(candidate))

candidate_with_email_and_phone = models(**candidate_dict).flatmap(
    generate_email_and_phone_registration)


class ModelTestCase(HypothesisTestCase):

    @given(candidate_with_phone, random_module())
    def test_phone(self, registration, dummy):
        self.assertTrue(registration.phone_number.is_valid())

    @given(candidate_with_email)
    def test_email(self, registration):
        self.assertFalse(registration.phone_number)

    @given(candidate_with_email_and_phone, random_module())
    def test_email_and_phone(self, registration, dummy):
        if registration.phone_number:
            self.assertTrue(registration.phone_number.is_valid())

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(lists(candidate), random_module())
    def test_valid_phone_number(self, registrations, dummy):
        self.assertFalse(User_Registration.objects.count())

    # ToDo: fix this test (it seems that it is only
    #       due to an error in code for testing)
    # @settings(suppress_health_check=[HealthCheck.too_slow])
    # @given(lists(candidate_with_email_and_phone))
    # def test_registrations_and_candidates(self, candidates):
    #     self.assertEqual(Candidate.objects.count(),
    #                      User_Registration.objects.count())

#     @settings(suppress_health_check=[HealthCheck.too_slow])
#     @given(registration_strategy)
#     def test_number_of_candidates(self, registrations):
#         """Testing the nested strategy."""
#         self.assertEqual(len(registrations), Candidate.total_in_line())

#     @settings(suppress_health_check=[HealthCheck.too_slow])
#     @given(lists(candidate_with_email_and_phone),
#            lists(candidate_with_email),
#            lists(candidate_with_phone),
#            lists(candidate),
#            random_module())
#     def test_unique_identifiers(self, c1, c2, c3, c4, dummy):
#         """Identifiers of registration shall be unique."""
#         identifier_set = set(User_Registration.objects.values_list(
#             'identifier', flat=True))
#         self.assertEqual(
#             len(identifier_set), User_Registration.objects.count())
