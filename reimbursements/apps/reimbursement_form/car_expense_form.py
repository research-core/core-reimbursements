from pyforms_web.organizers import segment

from .expense_form import ExpenseForm
from reimbursements.models import CarExpense

class CarExpenseForm(ExpenseForm):

    MODEL = CarExpense

    FIELDSETS = [
        ('document_number', "requisition_number"),
        ' ',
        ('_costcenter', '_financeprj', 'expensecode'),
        ('eur_value', ' ', ' '),
        ' ',
        'h3: Travel information',
        segment(
            'purpose',
            ('local', 'distance'),
        ),
        'description'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        return v.carexpense if v else v