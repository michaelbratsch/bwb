from django.db import models
from django.utils import timezone

import os

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
    def create(cls, candidate, form_data):
        data_list = [(key, val) for key, val in form_data.iteritems()]
        data_list.append(os.urandom(10)) # make the hash unique
        identifier = hash(frozenset(data_list))
        return cls(identifier = identifier,
                   candidate  = candidate)

    def __str__(self):
        return " ".join((self.identifier, str(self.candidate)))
