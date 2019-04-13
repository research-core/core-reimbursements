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
        "Amount",
        max_digits=11,
        decimal_places=2,
        default_currency="EUR",
        validators=[MinMoneyValidator(Money(0.01))],
    )
    reimbursement = models.ForeignKey(
        to="Reimbursement", on_delete=models.CASCADE, related_name="expenses"
    )

    def clean(self):
        if self.reimbursement.status != '0':
            raise ValidationError({
                "reimbursement": "The reimbursement is closed for edition. "
                                 "Change the status for pending if you would like to modify the expense."
            })

        if self.description is not None:
            # restrict number of lines
            nlines = self.description.count("\n")
            if nlines > 8 or len(self.description) > 600:
                raise ValidationError({"description": "Too much text."})

    def short_description(self):
        return textwrap.shorten(self.description, width=100, placeholder="...")
