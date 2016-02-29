from django.db import models
from django.utils import timezone

import os
import binascii

class Candidate(models.Model):
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email      = models.EmailField()

    def __str__(self):
        return " ".join((self.first_name, self.last_name, self.email))


class CandidateMetaData(models.Model):
    candidate = models.OneToOneField(
        Candidate,
        on_delete   = models.CASCADE,
        primary_key = True,
    )
    identifier       = models.CharField(max_length=100)

    time_of_register = models.DateTimeField(default = timezone.now,
                                            blank   = True)

    email_validated          = models.BooleanField(default = False)
    time_of_email_validation = models.DateTimeField(default = timezone.now,
                                                    blank   = True)

    win_validated          = models.BooleanField(default = False)
    time_of_win_validation = models.DateTimeField(default = timezone.now,
                                                  blank   = True)

    @classmethod
    def create(cls, candidate):
        identifier = os.urandom(64)
        instance = cls(identifier = binascii.b2a_base64(identifier)[:20],
                       candidate  = candidate)
        instance.save()
        return instance

    def __str__(self):
        return " ".join((str(self.candidate), self.identifier))
