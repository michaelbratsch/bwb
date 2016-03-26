from django.db import models
from django.utils import timezone

import os
import hashlib


max_name_length = 100
identifier_length = 20


def get_hash_value():
    return hashlib.sha224(os.urandom(64)).hexdigest()[:identifier_length]


class Registration(models.Model):
    email = models.EmailField()
    email_validated = models.BooleanField(default=False)
    time_of_email_validation = models.DateTimeField(default=timezone.now,
                                                    blank=True)

    win_validated = models.BooleanField(default=False)
    time_of_win_validation = models.DateTimeField(default=timezone.now,
                                                  blank=True)

    time_of_registration = models.DateTimeField(default=timezone.now,
                                                blank=True)

    def validate_email(self):
        if not self.email_validated:
            self.email_validated = True
            self.time_of_email_validation = timezone.now()
            self.save()

    def __str__(self):
        return " ".join((str(self.candidate), self.email, self.identifier))


class Candidate(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE,
                                     related_name='candidates')

    identifier = models.CharField(default=get_hash_value,
                                  max_length=identifier_length,
                                  unique=True)

    first_name = models.CharField(max_length=max_name_length)
    last_name = models.CharField(max_length=max_name_length)

    received_bicycle = models.BooleanField(default=False)

    def number_in_line(self):
        cls = self.__class__
        for i, candidate in enumerate(cls.objects.all()):
            if self == candidate:
                return i+1
        assert False, "Could not find object"

    @classmethod
    def candidates_in_line(cls):
        return cls.objects.count()

    def __str__(self):
        return " ".join((self.first_name, self.last_name))
