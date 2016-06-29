from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import hashlib
import os
from phonenumber_field.modelfields import PhoneNumberField
from solo.models import SingletonModel

from bwb.settings import LANGUAGE_CODE
from register.email import get_url_parameter


MAX_NAME_LENGTH = 100
IDENTIFIER_LENGTH = 20


def get_hash_value():
    return hashlib.sha224(os.urandom(64)).hexdigest()[:IDENTIFIER_LENGTH]


def datetime_min():
    return timezone.make_aware(timezone.datetime.min,
                               timezone.get_default_timezone())


class HandoutEvent(models.Model):
    due_date = models.DateTimeField()

    def __unicode__(self):
        return str(self.due_date)

    @property
    def url_parameter(self):
        return get_url_parameter('event_id', self.id)


class Candidate(models.Model):
    first_name = models.CharField(max_length=MAX_NAME_LENGTH)
    last_name = models.CharField(max_length=MAX_NAME_LENGTH)

    date_of_birth = models.DateField()

    WITH_BICYCLE = 1
    INVITED = 2
    WAITING = 3
    LOOSE = 4
    NOT_SHOWING_UP = 5

    CANDIDATE_STATUS = (
        (WAITING, "waiting"),
        (INVITED, "invited"),
        (WITH_BICYCLE, "bicycle received"),
        (LOOSE, "loose"),
        (NOT_SHOWING_UP, "not showing up"))

    status = models.IntegerField(choices=CANDIDATE_STATUS,
                                 default=WAITING)

    def __unicode__(self):
        return "%s %s %s %s" % (self.status, self.first_name, self.last_name,
                                self.date_of_birth)

    @property
    def has_bicycle(self):
        """Does this Candidate have a bicycle."""
        try:
            return self.bicycle is not None  # pylint: disable=no-member
        except Bicycle.DoesNotExist:
            return False

    # ToDo: add missing statuses
    def get_status(self):
        number_of_invitations = self.invitations.count()
        if self.has_bicycle:
            return self.WITH_BICYCLE
        elif number_of_invitations > 0:
            return self.INVITED
        else:
            return self.WAITING

    def update_status(self):
        new_status = self.get_status()
        if self.status != new_status:
            self.status = new_status
            self.save()  # pylint: disable=no-member

    @classmethod
    def get_status_and_candidates(cls):
        return [(val, cls.objects.filter(status=key).all())
                for key, val in cls.CANDIDATE_STATUS]

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
        return [candidate for candidate in registered
                if candidate.user_registration.bicycle_kind == kind]

    @classmethod
    def get_matching(cls, first_name, last_name, date_of_birth):
        """Return all Candidates with the same name and date of birth.
        The matching of the name is case-insensitive."""
        return cls.objects.filter(date_of_birth=date_of_birth,
                                  first_name__iexact=first_name,
                                  last_name__iexact=last_name)


class UserRegistration(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE,
                                     related_name='user_registration')

    language = models.CharField(default=LANGUAGE_CODE,
                                max_length=10)

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
                                  max_length=IDENTIFIER_LENGTH,
                                  primary_key=True)

    email = models.EmailField(blank=True)
    email_validated = models.BooleanField(default=False)
    time_of_email_validation = models.DateTimeField(default=datetime_min)

    mobile_number = PhoneNumberField(blank=True, default='', null=True)

    date_of_registration = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s %s %s %s " % (
            self.candidate, self.email, self.mobile_number,
            self.get_bicycle_kind_display())

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
            self.save()  # pylint: disable=no-member


class Invitation(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE,
                                  related_name='invitations')

    handout_event = models.ForeignKey(HandoutEvent,
                                      on_delete=models.CASCADE,
                                      related_name='invitations')

    date_of_invitation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s %s' % (self.candidate, self.handout_event)


class Bicycle(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE,
                                     related_name='bicycle')

    bicycle_number = models.PositiveIntegerField()
    lock_combination = models.PositiveIntegerField()
    color = models.CharField(max_length=200)
    brand = models.CharField(max_length=200)
    general_remarks = models.TextField(default='')
    date_of_handout = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "bicycle number: %s, color: %s, brand: %s" % (
            self.bicycle_number, self.color, self.brand)

    @property
    def url_parameter(self):
        return get_url_parameter('bicycle_id', self.id)

    def short_str(self):
        return '#%s %s %s' % (
            self.bicycle_number, self.color, self.brand)

    @property
    def information(self):
        """Return the information stored for this bicycle."""
        add_info = "lock combination: %s, general remarks: %s" % (
            self.lock_combination, self.general_remarks)
        return '%s\n%s' % (self, add_info)


@receiver(post_save, sender=Candidate)
def handler_on_save(
        instance, **kwargs):  # pylint: disable=unused-argument
    instance.update_status()


@receiver(post_save, sender=UserRegistration)
def handler_on_registration_save(
        instance, **kwargs):  # pylint: disable=unused-argument
    instance.candidate.update_status()


@receiver(post_save, sender=Invitation)
def handler_on_invitation_save(
        instance, **kwargs):  # pylint: disable=unused-argument
    instance.candidate.update_status()


@receiver(post_save, sender=Bicycle)
def handler_on_bicycle_save(
        instance, **kwargs):  # pylint: disable=unused-argument
    instance.candidate.update_status()


class SiteConfiguration(SingletonModel):
    # so many people can be registered without a bicycle
    max_number_of_registrations = models.PositiveIntegerField(default=200)
    # maximum number of times people will be invited to events
    max_number_of_autoinvites = models.PositiveIntegerField(default=2)

    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(default="")

    def __unicode__(self):
        return "Site Configuration"
