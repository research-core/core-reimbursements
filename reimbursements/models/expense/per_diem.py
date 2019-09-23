from .expense import Expense
from django.db import models
from django_countries.fields import CountryField

class PerDiem(Expense):

    purpose  = models.CharField('Travel purpose', max_length=255)
    local    = models.CharField('Local', max_length=255, null=True, blank=True)
    country  = CountryField()
    n_nights = models.PositiveSmallIntegerField('Number of nights for reimbursement', default=0)

    start_working = models.DateField('First day in the meeting')
    end_working   = models.DateField('Last day in the meeting')
    prove_working = models.FileField('Certificate of attendance', null=True, blank=True)

    start_travel  = models.DateField('Departure')
    end_travel    = models.DateField('Arrival')
    boarding_pass = models.FileField('Boarding pass', null=True, blank=True)
