from pyforms_web.organizers import segment

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
        'h3: Travel information',
        segment(
            'purpose',
            ('local', 'country', 'n_nights'),
        ),
        'h3: Working days',
        segment(
            ('start_working', 'end_working'),
            'prove_working',
        ),
        'h3: Trip',
        segment(
            ('start_travel', 'end_travel'),
            'boarding_pass',
        ),
        'description'
    ]

    def __init__(self, *args, **kwargs):
        ExpenseForm.__init__(self, *args, **kwargs)

    @property
    def model_object(self):
        v = ExpenseForm.model_object.fget(self)
        return v.perdiem if v else v