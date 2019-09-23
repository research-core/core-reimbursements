from .expense import Expense
from django.db import models

class CarExpense(Expense):

    purpose  = models.CharField('Travel purpose', max_length=255)
    local    = models.CharField('Itinerary', max_length=255)

    distance = models.PositiveSmallIntegerField('Distance in Km')