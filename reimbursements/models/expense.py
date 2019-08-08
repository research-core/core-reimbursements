import textwrap, os

from django.db import models
from djmoney.money import Money
from djmoney.models.fields import MoneyField
from django.core.exceptions import ValidationError
from djmoney.models.validators import MinMoneyValidator

def user_directory_path(instance, filename):
    return os.path.join('reimbursements', 'expense', instance.reimbursement.person.auth_user.username, filename)

class Expense(models.Model):
    """Expense to be reimbursed."""

    # TODO add attachments

    document_number    = models.CharField('Document number', max_length=50, blank=True)
    requisition_number = models.IntegerField('Requisition number', blank=True, null=True)
    description        = models.TextField("Description")
    value              = MoneyField(
                            "Amount",
                            max_digits=11,
                            decimal_places=2,
                            default_currency="EUR",
                            validators=[MinMoneyValidator(Money(0.01))],
                         )
    eur_value          = models.DecimalField(
                            'Amount in EUR',
                            max_digits=11,
                            decimal_places=2
                         )

    is_social     = models.BooleanField('It is a social expense', default=False)
    receipt       = models.FileField('Receipt', upload_to=user_directory_path)
    receipt_date  = models.DateField('Receipt date', null=True, default=None)
    reimbursement = models.ForeignKey(to="Reimbursement", on_delete=models.CASCADE, related_name="expenses")
    expensecode   = models.ForeignKey(to='finance.ExpenseCode', on_delete=models.CASCADE, related_name="reimbursement_expenses",
                                           verbose_name='Expense code')


    class Meta:
        ordering = ('document_number',)
        verbose_name = 'Reimbursement expense'
        verbose_name_plural = 'Reimbursements expenses'

    def clean(self):

        if self.description is not None:
            # restrict number of lines
            nlines = self.description.count("\n")
            if nlines > 8 or len(self.description) > 600:
                raise ValidationError({"description": "Too much text."})

    def short_description(self):
        return textwrap.shorten(self.description, width=100, placeholder="...")
