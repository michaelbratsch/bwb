from django.db import models
from django.utils import timezone

import os
import hashlib


max_name_length = 100
identifier_length = 20


def get_hash_value():
    return hashlib.sha224(os.urandom(64)).hexdigest()[:identifier_length]


def datetime_min():
    return timezone.make_aware(timezone.datetime.min,
                               timezone.get_default_timezone())


class Registration(models.Model):
    identifier = models.CharField(default=get_hash_value,
                                  max_length=identifier_length,
                                  unique=True)

    email = models.EmailField()
    email_validated = models.BooleanField(default=False)
    time_of_email_validation = models.DateTimeField(default=datetime_min,
                                                    blank=True)

    win_validated = models.BooleanField(default=False)
    time_of_win_validation = models.DateTimeField(default=datetime_min,
                                                  blank=True)

    time_of_registration = models.DateTimeField(default=timezone.now,
                                                blank=True)

    general_notes = models.TextField(default='', blank=True)

    def get_candidates(self):
        return self.candidates.all()

    def number_of_candidates(self):
        return self.candidates.count()

    def validate_email(self):
        if not self.email_validated:
            self.email_validated = True
            self.time_of_email_validation = timezone.now()
            self.save()

    def number_in_line(self):
        return max(c.number_in_line() for c in self.get_candidates())

    def __str__(self):
        candidate_names = ["'%s'" % i for i in self.get_candidates()]
        return " ".join(candidate_names + [self.identifier, self.email])


class Candidate(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE,
                                     related_name='candidates')

    first_name = models.CharField(max_length=max_name_length)
    last_name = models.CharField(max_length=max_name_length)

    received_bicycle = models.BooleanField(default=False)

    general_notes = models.TextField(default='', blank=True)

    def number_in_line(self):
        cls = self.__class__
        i = 0
        for candidate in cls.objects.all():
            if not candidate.received_bicycle:
                i += 1
            if self == candidate:
                return i
        assert False, "Could not find object"

    @classmethod
    def total_in_line(cls):
        return cls.objects.count()

    def __str__(self):
        return " ".join((self.first_name, self.last_name))
