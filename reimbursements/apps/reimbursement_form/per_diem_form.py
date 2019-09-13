from .expense_form import ExpenseForm
from reimbursements.models import PerDiem

class PerDiemForm(ExpenseForm):

    MODEL = PerDiem

    FIELDSETS = [
        ('document_number', "requisition_number", 'is_social'),
        ' ',
        ('_costcenter', '_financeprj', 'expensecode'),
        ('eur_value', "value", "value_currency"),
        ' ',
        ('receipt_date', ' ', ' '),
        'receipt',
        ' ',
        'purpose', 'local', 'country',
        'n_nights',
        'start_working',
        'end_working',
        'prove_working',
        'start_travel',
        'end_travel',
        'boarding_pass',

        'description'
    ]

    def __init__(self, *args, **kwargs):
        ExpenseForm.__init__(self, *args, **kwargs)