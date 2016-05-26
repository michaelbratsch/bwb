from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
import hashlib
import os

from django.utils.encoding import python_2_unicode_compatible

from register.email import get_url_parameter


max_name_length = 100
identifier_length = 20


def get_hash_value():
    return hashlib.sha224(os.urandom(64)).hexdigest()[:identifier_length]


def datetime_min():
    return timezone.make_aware(timezone.datetime.min,
                               timezone.get_default_timezone())


@python_2_unicode_compatible
class HandoutEvent(models.Model):
    due_date = models.DateTimeField()

    @property
    def url_parameter(self):
        return get_url_parameter('event_id', self.id)

    def __str__(self):
        return str(self.due_date)


@python_2_unicode_compatible
class Candidate(models.Model):
    first_name = models.CharField(max_length=max_name_length)
    last_name = models.CharField(max_length=max_name_length)

    date_of_birth = models.DateField()

    @property
    def has_bicycle(self):
        """Does this Candidate have a bicycle."""
        try:
            return self.bicycle is not None
        except Bicycle.DoesNotExist:
            return False

    # ToDo: introduce test that checks get_status with
    # get_status_and_candidates
    @property
    def get_status(self):
        number_of_inviations = self.invitations.count()
        if self.has_bicycle:
            return 'bicycle received'
        elif number_of_inviations:
            return 'invited %sx' % number_of_inviations
        else:
            return 'waiting'

    @classmethod
    def get_status_and_candidates(cls):
        """Returns a list of tuples which categorize all Candidates into
        the groups waiting, invited and bicycle received."""
        candidates_with_bicycles = set(Bicycle.objects.values_list(
            'candidate_id', flat=True))

        candidates_invited = set(Invitation.objects.values_list(
            'candidate_id', flat=True))
        candidates_invited -= candidates_with_bicycles

        candidates_waiting = set(
            Candidate.objects.values_list('id', flat=True))
        candidates_waiting -= candidates_with_bicycles | candidates_invited

        assert cls.objects.count() == (
            len(candidates_invited) + len(candidates_waiting) +
            len(candidates_with_bicycles))

        def get_objects(id_list):
            return cls.objects.in_bulk(id_list).values()

        return [('waiting', get_objects(candidates_waiting)),
                ('invited', get_objects(candidates_invited)),
                ('bicycle received', get_objects(candidates_with_bicycles))]

    @property
    def events_not_invited_to(self):
        """Return all events this person is NOT invited to."""
        event_ids_invited_to = self.invitations.all().values_list(
            'handout_event_id', flat=True)
        return HandoutEvent.objects.exclude(id__in=event_ids_invited_to)

    @classmethod
    def total_in_line(cls):
        """Number of all Candidates that do not have a bicycle."""
        return cls.objects.filter(bicycle__isnull=True).count()

    @classmethod
    def registered_and_without_bicycle(cls, kind):
        """Return all Candidates that do not have a bicycle and are registered
        for this kind of bicycle."""
        without_bicycles = cls.objects.filter(bicycle__isnull=True)
        registered = without_bicycles.filter(user_registration__isnull=False)
        return filter(lambda c: c.user_registration.bicycle_kind == kind,
                      registered)

    @classmethod
    def get_matching(cls, first_name, last_name, date_of_birth):
        """Return all Candidates with the same name and date of birth.
        The matching of the name is case-insensitive."""
        return cls.objects.filter(date_of_birth=date_of_birth,
                                  first_name__iexact=first_name,
                                  last_name__iexact=last_name)

    def __str__(self):
        return "%s %s %s" % (self.first_name, self.last_name,
                             self.date_of_birth)


@python_2_unicode_compatible
class User_Registration(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE,
                                     related_name='user_registration')

    # ToDo: remember language of registration to send invitation email
    # in right language

    MALE = 1
    FEMALE = 2
    CHILD_SMALL = 3
    CHILD_BIG = 4

    BICYCLE_CHOICES = (
        (MALE, "men's bicycle"), (FEMALE, "ladies' bicycle"),
        (CHILD_SMALL, "children's bicycle small"),
        (CHILD_BIG, "children's bicycle big"))

    bicycle_kind = models.IntegerField(choices=BICYCLE_CHOICES)

    identifier = models.CharField(default=get_hash_value,
                                  max_length=identifier_length,
                                  primary_key=True)

    email = models.EmailField(blank=True)
    email_validated = models.BooleanField(default=False)
    time_of_email_validation = models.DateTimeField(default=datetime_min)

    phone_number = PhoneNumberField(blank=True, default='', null=True)

    time_of_registration = models.DateTimeField(default=timezone.now)

    def number_in_line(self):
        """Current number of people in line waiting for this kind of
        bicycle."""
        cls = self.__class__
        i = 0
        for registration in cls.objects.filter(bicycle_kind=self.bicycle_kind):
            if not registration.candidate.has_bicycle:
                i += 1
            if self.candidate == registration.candidate:
                return i
        assert False, "Could not find object in database."

    def validate_email(self):
        """Flag email address for validated and store current time."""
        if not self.email_validated:
            self.email_validated = True
            self.time_of_email_validation = timezone.now()
            self.save()

    def __str__(self):
        return "%s %s %s %s " % (self.candidate, self.email, self.phone_number,
                                 self.get_bicycle_kind_display())


@python_2_unicode_compatible
class Invitation(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE,
                                  related_name='invitations')

    handout_event = models.ForeignKey(HandoutEvent,
                                      on_delete=models.CASCADE,
                                      related_name='invitations')

    time_of_invitation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s %s' % (self.candidate, self.handout_event)


@python_2_unicode_compatible
class Bicycle(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE,
                                     related_name='bicycle')

    bicycle_number = models.PositiveIntegerField()
    lock_combination = models.PositiveIntegerField()
    color = models.CharField(max_length=200)
    brand = models.CharField(max_length=200)
    general_remarks = models.TextField(default='')

    @property
    def url_parameter(self):
        return get_url_parameter('bicycle_id', self.id)

    def __str__(self):
        return "bicycle number: %s, color: %s, brand: %s" % (
            self.bicycle_number, self.color, self.brand)

    def short_str(self):
        return '#%s %s %s' % (
            self.bicycle_number, self.color, self.brand)

    @property
    def information(self):
        """Return the information stored for this bicycle."""
        add_info = "lock combination: %s, general remarks: %s" % (
            self.lock_combination, self.general_remarks)
        return '%s\n%s' % (self, add_info)
