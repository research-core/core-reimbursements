from pyforms_web.organizers import segment

from .expense_form import ExpenseForm
from reimbursements.models import PerDiem

class PerDiemForm(ExpenseForm):

    MODEL = PerDiem

    FIELDSETS = [
        ('document_number', "requisition_number"),
        ' ',
        ('_costcenter', '_financeprj', 'expensecode'),
        ('eur_value', ' ', ' '),
        ' ',
        'h3: Travel information',
        segment(
            'purpose',
            ('local', 'country', 'n_nights'),
        ),
        'h3: Meeting dates',
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

    def update_value_evt(self):
        pass

    def update_object_fields(self, obj):
        super().update_object_fields(obj)
        obj.value = self.eur_value.value
        obj.value_currency = 'EUR'
        return obj

    @property
    def model_object(self):
        v = ExpenseForm.model_object.fget(self)
        return v.perdiem if v else v