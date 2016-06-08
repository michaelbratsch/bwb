import phonenumbers

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from faker import Faker
from hypothesis import given, settings, HealthCheck
from hypothesis.extra.django import TestCase as HypothesisTestCase
from hypothesis.extra.django.models import models
from hypothesis.strategies import integers, random_module
from hypothesis.strategies import just, text, builds, lists, sampled_from

from register.forms import parse_mobile_number, MOBILE_PHONE_PREFIXES
from register.models import Candidate, UserRegistration, MAX_NAME_LENGTH


# filter text that only contains of whitespace
name_strategy = text(min_size=1, max_size=MAX_NAME_LENGTH).filter(lambda x:
                                                                  x.strip())
date_strategy = builds(target=Faker('de').date)

bicycle_kind_strategy = sampled_from(
    [value for value, name in UserRegistration.BICYCLE_CHOICES])


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


def create_mobile_number():
    prefix = sampled_from(MOBILE_PHONE_PREFIXES).example()
    number_strat = integers(min_value=1000000, max_value=99999999)
    counter = 0
    while True:
        number = number_strat.example()
        mobile_number = '%s%s' % (prefix, number)

        try:
            return parse_mobile_number(mobile_number)
        except ValidationError:
            pass

        counter += 1
        assert counter < 10000, 'No number matching for prefix ' + prefix


# this is just a verifier
def valid_mobile_number(number):
    parsed_number = phonenumbers.parse(number, 'DE')

    assert phonenumbers.is_valid_number_for_region(
        parsed_number, 'de'), parsed_number
    return True

phone_strategy = builds(target=create_mobile_number)
phone_strategy_clean = phone_strategy.filter(lambda x:
                                             valid_mobile_number(x))

candidate_dict = {'model': Candidate,
                  'first_name': name_strategy,
                  'last_name': name_strategy,
                  'date_of_birth': date_strategy}

candidate = models(**candidate_dict)


def generate_email_registration(candidate):
    return models(model=UserRegistration,
                  email=email_strategy,
                  candidate=just(candidate))

candidate_with_email = models(**candidate_dict).flatmap(
    generate_email_registration)


def generate_phone_registration(candidate):
    return models(model=UserRegistration,
                  mobile_number=phone_strategy_clean,
                  candidate=just(candidate))

candidate_with_phone = models(**candidate_dict).flatmap(
    generate_phone_registration)


def generate_email_and_phone_registration(candidate):
    return models(model=UserRegistration,
                  email=email_strategy,
                  mobile_number=phone_strategy_clean,
                  candidate=just(candidate))

candidate_with_email_and_phone = models(**candidate_dict).flatmap(
    generate_email_and_phone_registration)


class ModelTestCase(HypothesisTestCase):

    @given(candidate_with_phone, random_module())
    def test_phone(self, registration, dummy):
        self.assertTrue(registration.mobile_number.is_valid())

    @given(candidate_with_email)
    def test_email(self, registration):
        self.assertFalse(registration.mobile_number)

    @given(candidate_with_email_and_phone, random_module())
    def test_email_and_phone(self, registration, dummy):
        if registration.mobile_number:
            self.assertTrue(registration.mobile_number.is_valid())

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(lists(candidate), random_module())
    def test_valid_mobile_number(self, registrations, dummy):
        self.assertFalse(UserRegistration.objects.count())

    # ToDo: fix this test (it seems that it is only
    #       due to an error in code for testing)
    # @settings(suppress_health_check=[HealthCheck.too_slow])
    # @given(lists(candidate_with_email_and_phone))
    # def test_registrations_and_candidates(self, candidates):
    #     self.assertEqual(Candidate.objects.count(),
    #                      UserRegistration.objects.count())

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
#         identifier_set = set(UserRegistration.objects.values_list(
#             'identifier', flat=True))
#         self.assertEqual(
#             len(identifier_set), UserRegistration.objects.count())
