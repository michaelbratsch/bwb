from django.db import models
from django.utils import timezone

import os
import hashlib


def getHashValue():
    return hashlib.sha224(os.urandom(64)).hexdigest()[:20]


class Registration(models.Model):
    identifier = models.CharField(default=getHashValue, max_length=100,
                                  unique=True)

    time_of_register = models.DateTimeField(default=timezone.now, blank=True)

    email_validated = models.BooleanField(default=False)
    time_of_email_validation = models.DateTimeField(default=timezone.now,
                                                    blank=True)

    win_validated = models.BooleanField(default=False)
    time_of_win_validation = models.DateTimeField(default=timezone.now,
                                                  blank=True)

    def validate_email(self):
        if not self.email_validated:
            self.email_validated = True
            self.time_of_email_validation = timezone.now()
            self.save()

    def number_in_line(self):
        cls = self.__class__
        for i, candidate in enumerate(cls.objects.all()):
            if self == candidate:
                return i+1
        assert False, "Could not find object"

    @classmethod
    def total_candidates_in_line(cls):
        return cls.objects.count()

    def __str__(self):
        return " ".join((str(self.candidate), self.identifier))


class Candidate(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()

    received_bicycle = models.BooleanField(default=False)

    def __str__(self):
        return " ".join((self.first_name, self.last_name, self.email))
