import textwrap

from django.db import models
from djmoney.money import Money
from djmoney.models.fields import MoneyField
from django.core.exceptions import ValidationError
from djmoney.models.validators import MinMoneyValidator

class Expense(models.Model):
    """Expense to be reimbursed."""

    # TODO add attachments

    document_number = models.CharField('Document number', max_length=50, blank=True)
    requisition_number = models.IntegerField('Requisition number', blank=True, null=True)
    description = models.TextField("Description")
    value = MoneyField(
        "Currency",
        max_digits=11,
        decimal_places=2,
        default_currency="EUR",
        validators=[MinMoneyValidator(Money(0.01))],
    )
    reimbursement = models.ForeignKey(
        to="Reimbursement", on_delete=models.CASCADE, related_name="expenses"
    )

    def clean(self):
        self.description = self.description.strip("\n")

        # restrict number of lines
        new_lines = len(self.description.split("\n"))
        if new_lines > 8 or len(self.description) > 600:
            raise ValidationError({"description": "Too much text."})

    def short_description(self):
        return textwrap.shorten(self.description, width=100, placeholder="...")
